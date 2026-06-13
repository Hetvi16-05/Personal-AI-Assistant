from sqlalchemy.orm import Session
from app.models import User, Goal, Task, Project, UserMemory
from app.models.task import TaskStatus


class MemoryService:
    """
    Loads all user context and assembles it into a structured string
    that is injected into every LLM prompt for personalization.
    """

    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def get_user(self) -> User | None:
        return self.db.query(User).filter(User.id == self.user_id).first()

    def get_active_goals(self) -> list[Goal]:
        return self.db.query(Goal).filter(
            Goal.user_id == self.user_id,
            Goal.status == "active"
        ).all()

    def get_pending_tasks(self) -> list[Task]:
        return self.db.query(Task).filter(
            Task.user_id == self.user_id,
            Task.status.in_([TaskStatus.pending, TaskStatus.in_progress])
        ).all()

    def get_active_projects(self) -> list[Project]:
        return self.db.query(Project).filter(
            Project.user_id == self.user_id,
            Project.status == "active"
        ).all()

    def get_memories(self, limit: int = 20) -> list[UserMemory]:
        return self.db.query(UserMemory).filter(
            UserMemory.user_id == self.user_id
        ).order_by(UserMemory.created_at.desc()).limit(limit).all()

    def build_context(self) -> str:
        """Return a full user context string for LLM prompts."""
        user = self.get_user()
        if not user:
            return "No user profile found."

        goals = self.get_active_goals()
        tasks = self.get_pending_tasks()
        projects = self.get_active_projects()
        memories = self.get_memories()

        lines = [
            f"## User Profile",
            f"Name: {user.name}",
            f"Skills: {user.skills or 'Not specified'}",
            f"Interests: {user.interests or 'Not specified'}",
            f"Preferences: {user.preferences or 'None'}",
            "",
            "## Active Goals",
        ]

        if goals:
            for g in goals:
                deadline = g.deadline.strftime("%Y-%m-%d") if g.deadline else "No deadline"
                lines.append(f"- [{g.id}] {g.title} (Deadline: {deadline})")
        else:
            lines.append("- No active goals")

        lines += ["", "## Active Projects"]
        if projects:
            for p in projects:
                lines.append(f"- [{p.id}] {p.title}")
        else:
            lines.append("- No active projects")

        lines += ["", "## Pending Tasks"]
        if tasks:
            for t in tasks:
                deadline = t.deadline.strftime("%Y-%m-%d") if t.deadline else "No deadline"
                lines.append(
                    f"- [{t.id}] {t.title} | "
                    f"Impact:{t.impact_score} Urgency:{t.urgency_score} "
                    f"Effort:{t.effort_score} Align:{t.alignment_score} "
                    f"(Deadline: {deadline})"
                )
        else:
            lines.append("- No pending tasks")

        lines += ["", "## Recent Memory"]
        if memories:
            for m in memories:
                lines.append(f"- {m.content}")
        else:
            lines.append("- No memory entries")

        return "\n".join(lines)

    def add_memory(self, content: str, tags: str = "", source: str = "chat") -> UserMemory:
        mem = UserMemory(
            user_id=self.user_id,
            content=content,
            tags=tags,
            source=source
        )
        self.db.add(mem)
        self.db.commit()
        self.db.refresh(mem)
        return mem
