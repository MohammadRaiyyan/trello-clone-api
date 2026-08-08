import uuid

from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.organization import Organization, OrganizationMember, OrgRole
from src.schemas.organization import CreateOrganization
from src.utils.slug import generate_slug


class OrganizationService:
    async def get_user_organizations(
        self, user_id: uuid.UUID, session: AsyncSession
    ) -> list[tuple[Organization, OrganizationMember]]:
        statement = (
            select(Organization, OrganizationMember)
            .join(
                OrganizationMember,
                col(OrganizationMember.organization_id == Organization.id),
            )
            .where(col(OrganizationMember.user_id == user_id))
        )
        restult = await session.exec(statement)
        return list(restult.all())

    async def create_organization(
        self, user_id: uuid.UUID, new_org: CreateOrganization, session: AsyncSession
    ) -> Organization:
        organization = Organization(
            created_by=user_id,
            name=new_org.name,
            logo_url=new_org.logo_url,
            description=new_org.description,
            slug=generate_slug(new_org.name),
        )
        session.add(organization)
        await session.flush()
        await self._create_organization_member(
            user_id=user_id, org_id=organization.id, session=session
        )
        await session.commit()
        await session.refresh(organization)
        return organization

    async def _create_organization_member(
        self, user_id: uuid.UUID, org_id: uuid.UUID, session: AsyncSession
    ) -> None:
        organization_member = OrganizationMember(
            user_id=user_id, organization_id=org_id, role=OrgRole.OWNER
        )
        session.add(organization_member)
