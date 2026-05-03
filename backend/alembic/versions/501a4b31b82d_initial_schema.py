"""initial_schema

Revision ID: 501a4b31b82d
Revises: 
Create Date: 2026-05-02 20:12:07.276137

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '501a4b31b82d'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "genotypes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), unique=True, nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("zygosity", sa.String(50), nullable=True),
    )

    op.create_table(
        "cages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("label", sa.String(100), unique=True, nullable=False),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("capacity", sa.Integer(), nullable=False, server_default="5"),
    )

    mouse_status = sa.Enum("Alive", "Deceased", "Culled", name="mousestatus")
    sex_enum = sa.Enum("Male", "Female", name="sex")

    op.create_table(
        "mice",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ear_tag", sa.String(50), unique=True, nullable=False),
        sa.Column("sex", sex_enum, nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=False),
        sa.Column("status", mouse_status, nullable=False, server_default="Alive"),
        sa.Column("sire_id", sa.Integer(), sa.ForeignKey("mice.id"), nullable=True),
        sa.Column("dam_id", sa.Integer(), sa.ForeignKey("mice.id"), nullable=True),
        sa.Column("genotype_id", sa.Integer(), sa.ForeignKey("genotypes.id"), nullable=True),
        sa.Column("cage_id", sa.Integer(), sa.ForeignKey("cages.id"), nullable=True),
    )

    study_status = sa.Enum("Draft", "Active", "Completed", name="studystatus")

    op.create_table(
        "studies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("status", study_status, nullable=False, server_default="Draft"),
    )

    op.create_table(
        "cohorts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("study_id", sa.Integer(), sa.ForeignKey("studies.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
    )

    op.create_table(
        "enrollments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cohort_id", sa.Integer(), sa.ForeignKey("cohorts.id"), nullable=False),
        sa.Column("mouse_id", sa.Integer(), sa.ForeignKey("mice.id"), nullable=False),
        sa.Column("enrolled_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("removed_at", sa.DateTime(), nullable=True),
        sa.Column("removal_reason", sa.Text(), nullable=True),
    )

    op.create_table(
        "measurements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("enrollment_id", sa.Integer(), sa.ForeignKey("enrollments.id"), nullable=False),
        sa.Column("recorded_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("tumor_length_mm", sa.Float(), nullable=True),
        sa.Column("tumor_width_mm", sa.Float(), nullable=True),
        sa.Column("tumor_volume_mm3", sa.Float(), nullable=True),
        sa.Column("body_weight_g", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("measurements")
    op.drop_table("enrollments")
    op.drop_table("cohorts")
    op.drop_table("studies")
    op.drop_table("mice")
    op.drop_table("cages")
    op.drop_table("genotypes")
    sa.Enum(name="studystatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="mousestatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="sex").drop(op.get_bind(), checkfirst=True)
