import {
  Badge,
  Box,
  Heading,
  HStack,
  Skeleton,
  Text,
  VStack,
  Button,
} from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
// import { FiEdit3, FiTrash2 } from "react-icons/fi"

import { SurveyTemplatesService } from "@/client"
import type { SurveyTemplatePublic } from "@/client"
import useCustomToast from "@/hooks/useCustomToast"
import ManageQuestions from "./ManageQuestions"
// import EditSurveyTemplate from "./EditSurveyTemplate"

interface SurveyTemplatesListProps {
  surveyTemplates: SurveyTemplatePublic[]
  isLoading: boolean
}

export default function SurveyTemplatesList({ surveyTemplates, isLoading }: SurveyTemplatesListProps) {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  // const [editingTemplate, setEditingTemplate] = useState<SurveyTemplatePublic | null>(null)

  const activateMutation = useMutation({
    mutationFn: (id: string) => SurveyTemplatesService.activateSurveyTemplate({ surveyTemplateId: id }),
    onSuccess: () => {
      showSuccessToast("Survey template activated successfully.")
      queryClient.invalidateQueries({ queryKey: ["survey-templates"] })
    },
    onError: () => {
      showErrorToast("Failed to activate survey template.")
    },
  })

  const deactivateMutation = useMutation({
    mutationFn: (id: string) => SurveyTemplatesService.deactivateSurveyTemplate({ surveyTemplateId: id }),
    onSuccess: () => {
      showSuccessToast("Survey template deactivated successfully.")
      queryClient.invalidateQueries({ queryKey: ["survey-templates"] })
    },
    onError: () => {
      showErrorToast("Failed to deactivate survey template.")
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => SurveyTemplatesService.deleteSurveyTemplate({ surveyTemplateId: id }),
    onSuccess: () => {
      showSuccessToast("Survey template deleted successfully.")
      queryClient.invalidateQueries({ queryKey: ["survey-templates"] })
    },
    onError: () => {
      showErrorToast("Failed to delete survey template.")
    },
  })

  // const handleSurveyTemplateUpdated = () => {
  //   queryClient.invalidateQueries({ queryKey: ["survey-templates"] })
  //   setEditingTemplate(null)
  // }

  const getQuestionCount = (questions: Record<string, any>) => {
    if (!questions || typeof questions !== 'object') return 0
    return Object.keys(questions).length
  }

  if (isLoading) {
    return (
      <VStack gap={4} align="stretch">
        {Array.from({ length: 3 }).map((_, i) => (
          <Box key={i} p={4} borderWidth={1} borderRadius="md">
            <VStack align="start" gap={3}>
              <Skeleton height="24px" width="70%" />
              <Skeleton height="16px" width="100%" />
              <Skeleton height="16px" width="60%" />
            </VStack>
          </Box>
        ))}
      </VStack>
    )
  }

  if (surveyTemplates.length === 0) {
    return (
      <Box textAlign="center" py={10}>
        <Text fontSize="lg" color="gray.600">
          No survey templates found. Create your first template to get started.
        </Text>
      </Box>
    )
  }

  return (
    <VStack gap={4} align="stretch">
      {surveyTemplates.map((template) => (
        <Box key={template.id} p={4} borderWidth={1} borderRadius="md" bg="white" shadow="sm">
          <VStack align="stretch" gap={3}>
            <HStack justify="space-between">
              <VStack align="start" gap={1} flex={1}>
                <Heading size="md">
                  {template.name}
                </Heading>
                <HStack>
                  <Badge colorPalette={template.active ? "green" : "gray"}>
                    {template.active ? "Active" : "Inactive"}
                  </Badge>
                  <Text fontSize="sm" color="gray.600">
                    v{template.version}
                  </Text>
                </HStack>
              </VStack>
              <HStack gap={2}>
                {template.active ? (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => deactivateMutation.mutate(template.id)}
                    loading={deactivateMutation.isPending}
                    style={{ color: "#006496" }}
                  >
                    Deactivate
                  </Button>
                ) : (
                  <Button
                    size="sm"
                    colorPalette="green"
                    onClick={() => activateMutation.mutate(template.id)}
                    loading={activateMutation.isPending}
                  >
                    Activate
                  </Button>
                )}
                <Button
                  size="sm"
                  variant="outline"
                  colorPalette="red"
                  onClick={() => {
                    if (confirm("Are you sure you want to delete this survey template?")) {
                      deleteMutation.mutate(template.id)
                    }
                  }}
                  loading={deleteMutation.isPending}
                >
                  Delete
                </Button>
              </HStack>
            </HStack>
            
            <Text color="gray.600" fontSize="sm">
              {template.description || "No description"}
            </Text>
            
            <HStack justify="space-between">
              <Text fontSize="sm" fontWeight="medium">
                {getQuestionCount(template.questions)} questions
              </Text>
              <HStack gap={2}>
                <ManageQuestions template={template} />
                <Text fontSize="sm" color="gray.500">
                  Created {new Date(template.created_at).toLocaleDateString()}
                </Text>
              </HStack>
            </HStack>
          </VStack>
        </Box>
      ))}
    </VStack>
  )
}
