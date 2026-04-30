import asyncio
import time
from datetime import datetime, timezone
from app.models.run import TestRun, StepResult, RunStatus
from app.core.assertions import run_assertion, AssertionContext
from app.core.bluebubbles import BlueBubblesClient, find_chat_by_number
from app.config import settings
from app.database import engine
from sqlmodel import Session
from app.core.scenario_parser import load_scenario


async def execute_run(run_id: int):
    with Session(engine) as session:
        run = session.get(TestRun, run_id)
        if not run:
            return

        try:
            scenario = load_scenario(run.scenario_file)
        except Exception as e:
            run.status = RunStatus.failed
            session.add(run)
            session.commit()
            return

        run.status = RunStatus.running
        session.add(run)
        session.commit()

        try:
            bb_client = BlueBubblesClient(
                settings.bluebubbles_url, settings.bluebubbles_password
            )
            chat = find_chat_by_number(bb_client, run.bot_number)
            if not chat:
                run.status = RunStatus.failed
                session.add(run)
                session.commit()
                print(
                    f"Failed to find BlueBubbles chat for bot number {run.bot_number}"
                )
                return

            chat_guid = chat["guid"]

            seen_guids = set()
            existing_messages = bb_client.get_chat_messages(chat_guid, limit=20)
            seen_guids.update(
                msg["guid"] for msg in existing_messages if msg.get("guid")
            )

        except Exception as e:
            run.status = RunStatus.failed
            session.add(run)
            session.commit()
            print(f"BlueBubbles initialization error: {e}")
            return

        all_passed = True

        for index, step in enumerate(scenario.steps):
            step_result = StepResult(
                test_run_id=run.id,
                step_index=index,
                message_sent=step.message,
                status=RunStatus.running,
            )
            session.add(step_result)
            session.commit()

            if step.delay_ms > 0:
                await asyncio.sleep(step.delay_ms / 1000.0)

            try:
                bb_client.send_text(chat_guid, step.message)
            except Exception as e:
                step_result.status = RunStatus.failed
                step_result.failure_reasons = [
                    f"Failed to send message via BlueBubbles: {e}"
                ]
                all_passed = False
                session.add(step_result)
                session.commit()
                continue

            start_time = time.time()
            timeout_seconds = scenario.timeout_ms / 1000.0

            response_found = False
            response_text = ""
            response_reaction = None

            while time.time() - start_time < timeout_seconds:
                try:
                    messages = bb_client.get_chat_messages(chat_guid, limit=3)
                    for msg in reversed(messages):
                        guid = msg.get("guid")
                        if not guid or guid in seen_guids:
                            continue

                        seen_guids.add(guid)

                        if not msg.get("isFromMe"):
                            assoc_type = msg.get("associatedMessageType")

                            valid_string_reactions = [
                                "love",
                                "like",
                                "dislike",
                                "laugh",
                                "emphasize",
                                "question",
                            ]
                            if assoc_type and assoc_type in valid_string_reactions:
                                response_reaction = assoc_type
                                response_found = True
                                response_text = f"[{response_reaction} reaction]"
                                break

                            text = msg.get("text") or msg.get("message") or ""
                            if text:
                                response_found = True
                                response_text = text
                                break

                    if response_found:
                        break
                except Exception as e:
                    print(f"Error polling BlueBubbles: {e}")

                await asyncio.sleep(2)

            if response_found:
                latency_ms = int((time.time() - start_time) * 1000)
                step_result.response_received = response_text
                step_result.response_latency_ms = latency_ms

                context = AssertionContext(
                    response_text=response_text,
                    latency_ms=latency_ms,
                    reaction_type=response_reaction,
                )

                passed_assertions = []
                failed_assertions = []
                failure_reasons = []

                for assertion in step.assert_:
                    result = await run_assertion(assertion, context)
                    if result.passed:
                        passed_assertions.append(assertion.type.value)
                    else:
                        failed_assertions.append(assertion.type.value)
                        failure_reasons.append(
                            f"[{assertion.type.value}] {result.reason}"
                        )

                step_result.assertions_passed = passed_assertions
                step_result.assertions_failed = failed_assertions
                step_result.failure_reasons = failure_reasons

                if failed_assertions:
                    step_result.status = RunStatus.failed
                    all_passed = False
                else:
                    step_result.status = RunStatus.passed

            else:
                step_result.status = RunStatus.timeout
                step_result.failure_reasons = [
                    f"Timeout waiting for reply via BlueBubbles after {scenario.timeout_ms}ms"
                ]
                all_passed = False

            session.add(step_result)
            session.commit()

        run.status = RunStatus.passed if all_passed else RunStatus.failed
        run.finished_at = datetime.now(timezone.utc)
        session.add(run)
        session.commit()
