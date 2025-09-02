import {
  Box,
  Heading,
  Text,
  VStack,
  HStack,
  Badge,
} from "@chakra-ui/react"

interface PerformanceData {
  survey_performance: Array<{
    template_id: string
    template_name: string
    surveys_sent: number
    responses_received: number
    response_rate: number
    avg_completion_time: number
    avg_rating: number
    completion_rate: number
  }>
  total_templates: number
}

interface SurveyPerformanceProps {
  data?: PerformanceData
}

export default function SurveyPerformance({ data }: SurveyPerformanceProps) {
  if (!data) {
    return null
  }

  const { survey_performance } = data

  const getResponseRateColor = (rate: number) => {
    if (rate >= 80) return "green"
    if (rate >= 60) return "yellow"
    return "red"
  }

  const getRatingColor = (rating: number) => {
    if (rating >= 4.5) return "green"
    if (rating >= 3.5) return "yellow"
    return "red"
  }

  return (
    <Box
      p={6}
      bg="white"
      borderRadius="lg"
      shadow="sm"
      borderWidth={1}
      _hover={{ shadow: "md" }}
      transition="shadow 0.2s"
    >
      <VStack align="stretch" gap={4}>
        <Box>
          <Heading size="lg" mb={2}>
            Survey Performance
          </Heading>
          <Text color="gray.600" fontSize="sm">
            Performance metrics by survey template
          </Text>
        </Box>

        <VStack gap={4} align="stretch" maxHeight="400px" overflowY="auto">
          {survey_performance.map((survey) => (
            <Box
              key={survey.template_id}
              p={4}
              borderRadius="md"
              bg="gray.50"
              borderWidth={1}
              borderColor="gray.200"
            >
              <VStack align="stretch" gap={3}>
                {/* Header */}
                <HStack justify="space-between">
                  <VStack align="start" gap={1} flex={1}>
                    <Text fontWeight="semibold" fontSize="sm">
                      {survey.template_name}
                    </Text>
                    <HStack gap={4}>
                      <Text fontSize="xs" color="gray.500">
                        {survey.surveys_sent} sent
                      </Text>
                      <Text fontSize="xs" color="gray.500">
                        {survey.responses_received} responses
                      </Text>
                    </HStack>
                  </VStack>
                  <Badge
                    colorPalette={getResponseRateColor(survey.response_rate)}
                    size="sm"
                  >
                    {survey.response_rate}% response
                  </Badge>
                </HStack>

                {/* Response Rate Bar */}
                <Box>
                  <HStack justify="space-between" mb={1}>
                    <Text fontSize="xs" color="gray.600">
                      Response Rate
                    </Text>
                    <Text fontSize="xs" color="gray.600">
                      {survey.response_rate}%
                    </Text>
                  </HStack>
                  <Box
                    width="100%"
                    height="8px"
                    bg="gray.200"
                    borderRadius="full"
                    overflow="hidden"
                  >
                    <Box
                      width={`${survey.response_rate}%`}
                      height="100%"
                      bg={
                        getResponseRateColor(survey.response_rate) === "green" ? "#28a745" :
                        getResponseRateColor(survey.response_rate) === "yellow" ? "#ffc107" :
                        "#dc3545"
                      }
                      borderRadius="full"
                      transition="width 0.3s ease"
                    />
                  </Box>
                </Box>

                {/* Metrics Row */}
                <HStack justify="space-between" fontSize="xs">
                  <VStack gap={1}>
                    <Text color="gray.500">Avg Rating</Text>
                    <Badge
                      colorPalette={getRatingColor(survey.avg_rating)}
                      size="sm"
                    >
                      {survey.avg_rating}/5
                    </Badge>
                  </VStack>
                  <VStack gap={1}>
                    <Text color="gray.500">Completion</Text>
                    <Text fontWeight="semibold">
                      {survey.completion_rate}%
                    </Text>
                  </VStack>
                  <VStack gap={1}>
                    <Text color="gray.500">Avg Time</Text>
                    <Text fontWeight="semibold">
                      {survey.avg_completion_time}m
                    </Text>
                  </VStack>
                </HStack>
              </VStack>
            </Box>
          ))}
        </VStack>

        {survey_performance.length === 0 && (
          <Box textAlign="center" py={8}>
            <Text color="gray.500">
              No survey templates found. Create templates to see performance metrics.
            </Text>
          </Box>
        )}

        {/* Summary */}
        {survey_performance.length > 0 && (
          <Box pt={4} borderTop="1px" borderColor="gray.100">
            <HStack justify="space-between">
              <Text fontSize="sm" color="gray.600">
                Total Templates: {data.total_templates}
              </Text>
              <Text fontSize="sm" color="gray.600">
                Showing {Math.min(survey_performance.length, 5)} results
              </Text>
            </HStack>
          </Box>
        )}
      </VStack>
    </Box>
  )
}
