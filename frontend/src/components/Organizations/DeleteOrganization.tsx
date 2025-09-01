import { useMutation, useQueryClient } from "@tanstack/react-query"
import { FiTrash } from "react-icons/fi"

// TODO: Import from client after regenerating API client
// import { OrganizationsService } from "@/client"
// import type { ApiError } from "@/client/core/ApiError"
import useCustomToast from "@/hooks/useCustomToast"
// import { handleError } from "@/utils"
import {
  Button,
  DialogActionTrigger,
  DialogTitle,
  Flex,
  Text,
} from "@chakra-ui/react"
import { useState } from "react"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTrigger,
} from "../ui/dialog"
import { MenuItem } from "../ui/menu"

interface DeleteOrganizationProps {
  id: string
  name?: string
}

const DeleteOrganization = ({ id, name }: DeleteOrganizationProps) => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()

  const deleteOrganization = async (id: string) => {
    // TODO: Replace with actual API call after regenerating client
    // await OrganizationsService.deleteOrganization({ organizationId: id })
    
    // Mock API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    console.log("Mock: Deleting organization", id)
  }

  const mutation = useMutation({
    mutationFn: deleteOrganization,
    onSuccess: () => {
      showSuccessToast("Organization deleted successfully (Mock)")
      setIsOpen(false)
      queryClient.invalidateQueries({
        queryKey: ["organizations"],
      })
    },
    onError: () => {
      showSuccessToast("Error deleting organization")
    },
  })

  const onDelete = async () => {
    mutation.mutate(id)
  }

  return (
    <>
      <DialogRoot open={isOpen} onOpenChange={(e) => setIsOpen(e.open)}>
        <DialogTrigger asChild>
          <MenuItem
            value="delete"
            color="red.600"
            _hover={{
              bg: "red.600",
              color: "white",
            }}
            onClick={() => setIsOpen(true)}
          >
            <Flex gap={2}>
              <FiTrash />
              Delete Organization
            </Flex>
          </MenuItem>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Organization</DialogTitle>
          </DialogHeader>
          <DialogBody pb="4">
            <Text>
              Are you sure you want to delete the organization{" "}
              <Text as="span" fontWeight="bold">
                {name}
              </Text>
              ?
            </Text>
            <Text color="red.600" mt={2}>
              <Text as="span" fontWeight="bold">
                Warning:
              </Text>{" "}
              This action will permanently delete the organization and all associated data including users, surveys, and responses. This action cannot be undone.
            </Text>
          </DialogBody>
          <DialogFooter>
            <DialogActionTrigger asChild>
              <Button variant="outline" onClick={() => setIsOpen(false)}>
                Cancel
              </Button>
            </DialogActionTrigger>
            <Button
              colorScheme="red"
              onClick={onDelete}
              loading={mutation.isPending}
            >
              Delete
            </Button>
          </DialogFooter>
          <DialogCloseTrigger />
        </DialogContent>
      </DialogRoot>
    </>
  )
}

export default DeleteOrganization
