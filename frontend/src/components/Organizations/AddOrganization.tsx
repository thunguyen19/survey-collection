import { useMutation, useQueryClient } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"

// TODO: Import from client after regenerating API client
import { OrganizationsService } from "@/client"
// import type { ApiError } from "@/client/core/ApiError"
import useCustomToast from "@/hooks/useCustomToast"
// import { handleError } from "@/utils"

// Temporary type definition - replace with actual import
interface OrganizationCreate {
  name: string
  type?: string
  subscription_tier?: string
  settings?: Record<string, any>
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
import { FaPlus } from "react-icons/fa"
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

const AddOrganization = () => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isValid, isSubmitting },
  } = useForm<OrganizationCreate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      name: "",
      type: "",
      subscription_tier: "basic",
      settings: {},
      active: true,
    },
  })

  const mutation = useMutation({
    mutationFn: async (data: OrganizationCreate) => {
      // TODO: Replace with actual API call after regenerating client
      return OrganizationsService.createOrganization({ requestBody: data })
      
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      console.log("Mock: Creating organization", data)
      return { id: Date.now().toString(), ...data }
    },
    onSuccess: () => {
      showSuccessToast("Organization created successfully! (Mock)")
      reset()
      setIsOpen(false)
    },
    onError: () => {
      showSuccessToast("Error creating organization")
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["organizations"] })
    },
  })

  const onSubmit: SubmitHandler<OrganizationCreate> = (data) => {
    mutation.mutate(data)
  }

  return (
    <>
      <Flex py={8} gap={4}>
        <DialogRoot open={isOpen} onOpenChange={(e) => setIsOpen(e.open)}>
          <DialogTrigger asChild>
            <Button
              backgroundColor="#006496"
              variant="solid"
              gap="1"
              fontSize={{ base: "sm", md: "inherit" }}
              onClick={() => setIsOpen(true)}
            >
              <FaPlus /> Add Organization
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add Organization</DialogTitle>
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
              </VStack>
            </DialogBody>
            <DialogFooter>
              <DialogActionTrigger asChild>
                <Button backgroundColor="#006496" variant="outline" onClick={() => setIsOpen(false)}>
                  Cancel
                </Button>
              </DialogActionTrigger>
              <Button
                backgroundColor="#006496"
                variant="solid"
                onClick={handleSubmit(onSubmit)}
                loading={isSubmitting}
                disabled={!isValid}
              >
                Add
              </Button>
            </DialogFooter>
            <DialogCloseTrigger />
          </DialogContent>
        </DialogRoot>
      </Flex>
    </>
  )
}

export default AddOrganization
