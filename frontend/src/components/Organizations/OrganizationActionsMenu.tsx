import { IconButton } from "@chakra-ui/react"
import { BsThreeDotsVertical } from "react-icons/bs"
import { MenuContent, MenuRoot, MenuTrigger } from "../ui/menu"

import type { OrganizationPublic } from "@/client"
import DeleteOrganization from "./DeleteOrganization"
import EditOrganization from "./EditOrganization"

interface OrganizationActionsMenuProps {
  organization: OrganizationPublic
  disabled?: boolean
}

export const OrganizationActionsMenu = ({ organization, disabled }: OrganizationActionsMenuProps) => {
  return (
    <MenuRoot>
      <MenuTrigger asChild>
        <IconButton variant="ghost" color="inherit" disabled={disabled}>
          <BsThreeDotsVertical />
        </IconButton>
      </MenuTrigger>
      <MenuContent>
        <EditOrganization organization={organization} />
        <DeleteOrganization id={organization.id} name={organization.name} />
      </MenuContent>
    </MenuRoot>
  )
}
