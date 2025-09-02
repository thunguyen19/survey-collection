import {
  Button,
  Input,
  Textarea,
  VStack,
} from "@chakra-ui/react"
import { useMutation, useQuery } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"

import { SurveyTemplatesService, OrganizationsService, UsersService } from "@/client"
import type { SurveyTemplateCreate } from "@/client"
import useCustomToast from "@/hooks/useCustomToast"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle,
} from "../ui/dialog"
import { Field } from "../ui/field"
import { Checkbox } from "../ui/checkbox"

interface AddSurveyTemplateProps {
  open: boolean
  onClose: () => void
  onSurveyTemplateAdded: () => void
}

interface SurveyTemplateFormData {
  name: string
  description: string
  active: boolean
  organization_id: string
}

export default function AddSurveyTemplate({ 
  open, 
  onClose, 
  onSurveyTemplateAdded 
}: AddSurveyTemplateProps) {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  
  // Fetch organizations for the selector
  const { data: organizationsData, isLoading: organizationsLoading } = useQuery({
    queryKey: ["organizations"],
    queryFn: () => OrganizationsService.readOrganizations({ skip: 0, limit: 100 }),
  })

  const { data: currentUserData } = useQuery({
    queryKey: ["currentUser"],
    queryFn: () => UsersService.readUserMe(),
  })

  
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<SurveyTemplateFormData>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      name: "",
      description: "",
      active: false,
      organization_id: "",
    },
  })

  const mutation = useMutation({
    mutationFn: (data: SurveyTemplateCreate) => 
      SurveyTemplatesService.createSurveyTemplate({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Survey template created successfully.")
      reset()
      onSurveyTemplateAdded()
    },
    onError: (err: any) => {
      const errDetail = err.body?.detail || "Something went wrong."
      showErrorToast(`Failed to create survey template: ${errDetail}`)
    },
  })

  const onSubmit: SubmitHandler<SurveyTemplateFormData> = async (data) => {
    if (!data.organization_id) {
      showErrorToast("Please select an organization.")
      return
    }

    const surveyTemplateData: SurveyTemplateCreate = {
      name: data.name,
      description: data.description || null,
      active: data.active,
      version: 1,
      organization_id: data.organization_id,
      questions: {}, // Empty questions for MVP
      triggers: {},
      delivery_settings: {},
      created_by: currentUserData!.id,
    }

    mutation.mutate(surveyTemplateData)
  }

  const handleClose = () => {
    reset()
    onClose()
  }

  return (
    <DialogRoot open={open} onOpenChange={(e) => e.open ? undefined : handleClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create Survey Template</DialogTitle>
        </DialogHeader>
        <DialogCloseTrigger />
        
        <DialogBody>
          <form onSubmit={handleSubmit(onSubmit)}>
            <VStack gap={6} align="stretch">
              <Field
                label="Template Name"
                required
                invalid={!!errors.name}
                errorText={errors.name?.message}
              >
                <Input
                  {...register("name", {
                    required: "Template name is required.",
                    maxLength: {
                      value: 255,
                      message: "Template name must be 255 characters or less.",
                    },
                  })}
                  placeholder="Enter template name"
                />
              </Field>

              <Field label="Description">
                <Textarea
                  {...register("description")}
                  placeholder="Enter template description (optional)"
                  rows={3}
                />
              </Field>

              <Field
                label="Organization"
                required
                invalid={!!errors.organization_id}
                errorText={errors.organization_id?.message}
              >
                <select
                  {...register("organization_id", {
                    required: "Please select an organization.",
                  })}
                  disabled={organizationsLoading}
                  style={{
                    width: "100%",
                    padding: "8px 12px",
                    border: "1px solid #ccc",
                    borderRadius: "6px",
                    fontSize: "14px",
                    backgroundColor: "white"
                  }}
                >
                  <option value="">Select an organization</option>
                  {organizationsData?.data?.map((org: any) => (
                    <option key={org.id} value={org.id}>
                      {org.name}
                    </option>
                  )) || []}
                </select>
              </Field>

              <Field 
                label="Active Template"
                helperText="Active templates can be used to create feedback sessions"
              >
                <Checkbox
                  {...register("active")}
                >
                  Mark as active template
                </Checkbox>
              </Field>
            </VStack>
          </form>
        </DialogBody>

        <DialogFooter>
          <Button variant="ghost" onClick={handleClose}>
            Cancel
          </Button>
          <Button
            backgroundColor="#006496"
            onClick={handleSubmit(onSubmit)}
            loading={isSubmitting || mutation.isPending}
            loadingText="Creating..."
          >
            Create Template
          </Button>
        </DialogFooter>
      </DialogContent>
    </DialogRoot>
  )
}
