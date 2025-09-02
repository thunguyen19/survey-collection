import {
  Box,
  Heading,
  Text,
  VStack,
  HStack,
  Badge,
} from "@chakra-ui/react"
import { FiStar } from "react-icons/fi"

interface FeedbackData {
  recent_feedback: Array<{
    id: string
    survey_name: string
    submitted_at: string
    sentiment: string
    summary: string
    rating: number
    topics: string[]
  }>
  total_count: number
}

interface RecentFeedbackProps {
  data?: FeedbackData
}

export default function RecentFeedback({ data }: RecentFeedbackProps) {
  if (!data) {
    return null
  }

  const { recent_feedback } = data

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'green'
      case 'neutral': return 'yellow'
      case 'negative': return 'red'
      default: return 'gray'
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffHours / 24)

    if (diffHours < 1) return 'Just now'
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <FiStar
        key={i}
        size={14}
        color={i < rating ? "#ffc107" : "#e9ecef"}
        fill={i < rating ? "#ffc107" : "none"}
      />
    ))
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
            Recent Feedback
          </Heading>
          <Text color="gray.600" fontSize="sm">
            Latest survey responses with AI analysis
          </Text>
        </Box>

        <VStack gap={4} align="stretch" maxHeight="400px" overflowY="auto">
          {recent_feedback.map((feedback) => (
            <Box
              key={feedback.id}
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
                      {feedback.survey_name}
                    </Text>
                    <Text fontSize="xs" color="gray.500">
                      {formatDate(feedback.submitted_at)}
                    </Text>
                  </VStack>
                  <VStack align="end" gap={1}>
                    <Badge
                      colorPalette={getSentimentColor(feedback.sentiment)}
                      size="sm"
                    >
                      {feedback.sentiment}
                    </Badge>
                    <HStack gap={1}>
                      {renderStars(feedback.rating)}
                    </HStack>
                  </VStack>
                </HStack>

                {/* Summary */}
                <Text fontSize="sm" color="gray.700" lineHeight="1.4">
                  {feedback.summary}
                </Text>

                {/* Topics */}
                {feedback.topics.length > 0 && (
                  <HStack gap={2} flexWrap="wrap">
                    {feedback.topics.map((topic, index) => (
                      <Badge
                        key={index}
                        variant="outline"
                        colorPalette="blue"
                        size="sm"
                        fontSize="xs"
                      >
                        {topic}
                      </Badge>
                    ))}
                  </HStack>
                )}
              </VStack>
            </Box>
          ))}
        </VStack>

        {recent_feedback.length === 0 && (
          <Box textAlign="center" py={8}>
            <Text color="gray.500">
              No recent feedback available. Responses will appear here as they are submitted.
            </Text>
          </Box>
        )}

        {/* Footer */}
        {recent_feedback.length > 0 && (
          <Box pt={4} borderTop="1px" borderColor="gray.100">
            <HStack justify="space-between">
              <Text fontSize="sm" color="gray.600">
                Showing {recent_feedback.length} of {data.total_count} responses
              </Text>
              <Text fontSize="sm" color="#006496" cursor="pointer" _hover={{ textDecoration: "underline" }}>
                View all feedback
              </Text>
            </HStack>
          </Box>
        )}
      </VStack>
    </Box>
  )
}
