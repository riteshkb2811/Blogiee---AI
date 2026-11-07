import uuid
from langgraph.types import Command
from graph import app

EXIT_COMMANDS = {"exit", "bye", "quit", "end"}


def process_review_interrupt(config: dict) -> None:
    """
    Loops through pending interrupts, displays current progress
    (outline or draft) to the user, and resumes execution.
    """
    while True:
        state = app.get_state(config)

        # Exit loop when there are no more active interrupts
        if not state.tasks or not state.tasks[0].interrupts:
            break

        interrupt_data = state.tasks[0].interrupts[0].value
        question = interrupt_data.get("question", "Please review:")
        
        print(f"\n{'='*20} REVIEW REQUIRED {'='*20}")
        print(f"👉 {question}\n")

        if "research" in interrupt_data:
            print("--- Research Outline ---")
            print(interrupt_data["research"])
        elif "draft" in interrupt_data:
            print("--- Blog Draft ---")
            print(interrupt_data["draft"])

        print("-" * 57)
        review = input("Type 'approve' to proceed, or enter feedback to revise:\n> ").strip()

        if review.lower() == "approve":
            print("\n⏳ Feedback approved. Proceeding to next step...")
            app.invoke(Command(resume={}), config)
        else:
            print(f"\n⏳ Applying feedback: '{review}'...")
            app.invoke(Command(resume={"feedback": review}), config)


def generate_blog(topic: str, audience: str) -> None:
    """Runs the state graph for a single blog workflow."""
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    print("\n⏳ Initializing research...")
    app.invoke({"topic": topic, "audience": audience}, config)

    # Handle any interactive human-in-the-loop review steps
    process_review_interrupt(config)

    # Fetch and display the finalized blog
    final_state = app.get_state(config).values
    final_blog = final_state.get("final_draft", "No final draft was generated.")

    print(f"\n{'='*25} FINAL BLOG {'='*25}\n")
    print(final_blog)
    print(f"\n{'='*62}\n")


def main():
    print("=" * 45)
    print("               BLOGIEE AI                    ")
    print("=" * 45)

    while True:
        topic = input("\nEnter Blog Topic (or 'exit' to quit): ").strip()
        if not topic:
            continue
        if topic.lower() in EXIT_COMMANDS:
            print("\n👋 Bye! Hope you had fun creating blogs.")
            break

        audience = input("Enter Target Audience (default: General Audience): ").strip()
        if not audience:
            audience = "General Audience"

        generate_blog(topic, audience)


if __name__ == "__main__":
    main()