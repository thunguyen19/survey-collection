import {
  Box,
  Button,
  Container,
  Flex,
  Heading,
  Text,
  // VStack,
} from "@chakra-ui/react"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"

import { SurveyTemplatesService } from "@/client"
// import type { SurveyTemplatePublic } from "@/client"
import AddSurveyTemplate from "@/components/SurveyTemplates/AddSurveyTemplate"
import SurveyTemplatesList from "@/components/SurveyTemplates/SurveyTemplatesList"

export const Route = createFileRoute("/_layout/survey-templates")({
  component: SurveyTemplates,
})

function SurveyTemplates() {
  const queryClient = useQueryClient()
  const [showAddDialog, setShowAddDialog] = useState(false)
  
  const {
    data: surveyTemplates,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["survey-templates"],
    queryFn: () => SurveyTemplatesService.readSurveyTemplates(),
  })

  const handleSurveyTemplateAdded = () => {
    queryClient.invalidateQueries({ queryKey: ["survey-templates"] })
    setShowAddDialog(false)
  }

  return (
    <Container maxW="full">
      <Flex justify="space-between" align="center" mb={6}>
        <Box>
          <Heading size="lg" mb={2}>
            Survey Templates
          </Heading>
          <Text color="gray.600">
            Create and manage survey templates for patient feedback collection
          </Text>
        </Box>
        <Button
          backgroundColor="#006496"
          colorScheme="blue"
          onClick={() => setShowAddDialog(true)}
          size="lg"
        >
          Create Template
        </Button>
      </Flex>

      {isError ? (
        <Box textAlign="center" py={10}>
          <Text color="red.500" fontSize="lg">
            Something went wrong loading survey templates.
          </Text>
        </Box>
      ) : (
        <SurveyTemplatesList
          surveyTemplates={surveyTemplates?.data || []}
          isLoading={isLoading}
        />
      )}

      <AddSurveyTemplate
        open={showAddDialog}
        onClose={() => setShowAddDialog(false)}
        onSurveyTemplateAdded={handleSurveyTemplateAdded}
      />
    </Container>
  )
}

export default SurveyTemplates

