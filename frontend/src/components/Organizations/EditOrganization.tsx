import { useMutation, useQueryClient } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"
import { FiEdit } from "react-icons/fi"

// TODO: Import from client after regenerating API client
// import { type OrganizationPublic, type OrganizationUpdate, OrganizationsService } from "@/client"
// import type { ApiError } from "@/client/core/ApiError"
import useCustomToast from "@/hooks/useCustomToast"
// import { handleError } from "@/utils"

// Temporary type definitions - replace with actual imports
interface OrganizationPublic {
  id: string
  name: string
  type?: string
  subscription_tier?: string
  active: boolean
  created_at: string
  updated_at: string
}

interface OrganizationUpdate {
  name?: string
  type?: string
  subscription_tier?: string
  active?: boolean
}
import {
  Button,
  DialogActionTrigger,
  DialogTitle,
  Flex,
  Input,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useState } from "react"
import { Checkbox } from "../ui/checkbox"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTrigger,
} from "../ui/dialog"
import { Field } from "../ui/field"
import { MenuItem } from "../ui/menu"

interface EditOrganizationProps {
  organization: OrganizationPublic
}

const EditOrganization = ({ organization }: EditOrganizationProps) => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors, isValid, isSubmitting, isDirty },
  } = useForm<OrganizationUpdate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      name: organization.name,
      type: organization.type || "",
      subscription_tier: organization.subscription_tier || "basic",
      active: organization.active,
    },
  })

  const mutation = useMutation({
    mutationFn: async (data: OrganizationUpdate) => {
      // TODO: Replace with actual API call after regenerating client
      // return OrganizationsService.updateOrganization({
      //   organizationId: organization.id,
      //   requestBody: data,
      // })
      
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      console.log("Mock: Updating organization", organization.id, data)
      return { ...organization, ...data }
    },
    onSuccess: () => {
      showSuccessToast("Organization updated successfully! (Mock)")
      setIsOpen(false)
    },
    onError: () => {
      showSuccessToast("Error updating organization")
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["organizations"] })
    },
  })

  const onSubmit: SubmitHandler<OrganizationUpdate> = (data) => {
    mutation.mutate(data)
  }

  const onCancel = () => {
    reset()
    setIsOpen(false)
  }

  return (
    <>
      <DialogRoot open={isOpen} onOpenChange={(e) => setIsOpen(e.open)}>
        <DialogTrigger asChild>
          <MenuItem value="edit" onClick={() => setIsOpen(true)}>
            <Flex gap={2}>
              <FiEdit />
              Edit Organization
            </Flex>
          </MenuItem>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Organization</DialogTitle>
          </DialogHeader>
          <DialogBody pb="4">
            <VStack gap="4">
              <Field
                invalid={!!errors.name}
                errorText={errors.name?.message}
              >
                <Text fontWeight="bold">Name</Text>
                <Input
                  id="name"
                  {...register("name", {
                    required: "Organization name is required",
                    minLength: {
                      value: 2,
                      message: "Name must be at least 2 characters",
                    },
                  })}
                  placeholder="Organization Name"
                  type="text"
                />
              </Field>
              <Field
                invalid={!!errors.type}
                errorText={errors.type?.message}
              >
                <Text fontWeight="bold">Type</Text>
                <select
                  {...register("type")}
                  style={{
                    width: "100%",
                    padding: "8px",
                    borderRadius: "6px",
                    border: "1px solid #e2e8f0",
                    backgroundColor: "white",
                  }}
                >
                  <option value="">Select organization type</option>
                  <option value="hospital">Hospital</option>
                  <option value="clinic">Clinic</option>
                  <option value="medical_practice">Medical Practice</option>
                  <option value="healthcare_system">Healthcare System</option>
                  <option value="other">Other</option>
                </select>
              </Field>
              <Field>
                <Text fontWeight="bold">Subscription Tier</Text>
                <select
                  {...register("subscription_tier")}
                  style={{
                    width: "100%",
                    padding: "8px",
                    borderRadius: "6px",
                    border: "1px solid #e2e8f0",
                    backgroundColor: "white",
                  }}
                >
                  <option value="basic">Basic</option>
                  <option value="premium">Premium</option>
                  <option value="enterprise">Enterprise</option>
                </select>
              </Field>
              <Field>
                <Checkbox
                  {...register("active")}
                  checked={watch("active")}
                  onCheckedChange={(details) => setValue("active", !!details.checked)}
                >
                  Active
                </Checkbox>
              </Field>
            </VStack>
          </DialogBody>
          <DialogFooter>
            <DialogActionTrigger asChild>
              <Button variant="outline" onClick={onCancel}>
                Cancel
              </Button>
            </DialogActionTrigger>
            <Button
              variant="solid"
              onClick={handleSubmit(onSubmit)}
              loading={isSubmitting}
              disabled={!isValid || !isDirty}
            >
              Save
            </Button>
          </DialogFooter>
          <DialogCloseTrigger />
        </DialogContent>
      </DialogRoot>
    </>
  )
}

export default EditOrganization
