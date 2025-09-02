import {
  Box,
  Heading,
  Text,
  VStack,
  HStack,
  Badge,
} from "@chakra-ui/react"

interface SentimentData {
  sentiment_distribution: {
    positive: number
    neutral: number
    negative: number
  }
  top_topics: Array<{
    topic: string
    count: number
    avg_sentiment: string
  }>
  total_analyzed: number
  analysis_period: string
}

interface SentimentAnalysisProps {
  data?: SentimentData
}

export default function SentimentAnalysis({ data }: SentimentAnalysisProps) {
  if (!data) {
    return null
  }

  const { sentiment_distribution, top_topics, total_analyzed } = data

  // Calculate percentages
  const positivePercent = Math.round((sentiment_distribution.positive / total_analyzed) * 100)
  const neutralPercent = Math.round((sentiment_distribution.neutral / total_analyzed) * 100)
  const negativePercent = Math.round((sentiment_distribution.negative / total_analyzed) * 100)

  // Simple pie chart using SVG
  const size = 160
  const center = size / 2
  const radius = size / 2 - 10

  // Calculate angles for pie slices
  const positiveAngle = (sentiment_distribution.positive / total_analyzed) * 360
  const neutralAngle = (sentiment_distribution.neutral / total_analyzed) * 360
  const negativeAngle = (sentiment_distribution.negative / total_analyzed) * 360

  // Create SVG path for each slice
  const createArcPath = (startAngle: number, endAngle: number) => {
    const start = polarToCartesian(center, center, radius, endAngle)
    const end = polarToCartesian(center, center, radius, startAngle)
    const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1"
    
    return [
      "M", center, center,
      "L", start.x, start.y,
      "A", radius, radius, 0, largeArcFlag, 0, end.x, end.y,
      "Z"
    ].join(" ")
  }

  const polarToCartesian = (centerX: number, centerY: number, radius: number, angleInDegrees: number) => {
    const angleInRadians = (angleInDegrees - 90) * Math.PI / 180.0
    return {
      x: centerX + (radius * Math.cos(angleInRadians)),
      y: centerY + (radius * Math.sin(angleInRadians))
    }
  }

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return '#28a745'
      case 'neutral': return '#ffc107'
      case 'negative': return '#dc3545'
      default: return '#6c757d'
    }
  }

  const getSentimentColorPalette = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'green'
      case 'neutral': return 'yellow'
      case 'negative': return 'red'
      default: return 'gray'
    }
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
            Sentiment Analysis
          </Heading>
          <Text color="gray.600" fontSize="sm">
            Feedback sentiment breakdown
          </Text>
        </Box>

        {/* Pie Chart */}
        <Box display="flex" justifyContent="center" mb={4}>
          <svg width={size} height={size}>
            {/* Positive slice */}
            <path
              d={createArcPath(0, positiveAngle)}
              fill="#28a745"
              stroke="white"
              strokeWidth="2"
            />
            {/* Neutral slice */}
            <path
              d={createArcPath(positiveAngle, positiveAngle + neutralAngle)}
              fill="#ffc107"
              stroke="white"
              strokeWidth="2"
            />
            {/* Negative slice */}
            <path
              d={createArcPath(positiveAngle + neutralAngle, 360)}
              fill="#dc3545"
              stroke="white"
              strokeWidth="2"
            />
            
            {/* Center text */}
            <text
              x={center}
              y={center - 5}
              textAnchor="middle"
              fontSize="24"
              fontWeight="bold"
              fill="#333"
            >
              {total_analyzed}
            </text>
            <text
              x={center}
              y={center + 15}
              textAnchor="middle"
              fontSize="12"
              fill="#666"
            >
              Responses
            </text>
          </svg>
        </Box>

        {/* Legend */}
        <VStack gap={3}>
          <HStack justify="space-between" width="100%">
            <HStack>
              <Box w={3} h={3} bg="#28a745" borderRadius="full" />
              <Text fontSize="sm">Positive</Text>
            </HStack>
            <Text fontSize="sm" fontWeight="bold">
              {sentiment_distribution.positive} ({positivePercent}%)
            </Text>
          </HStack>
          <HStack justify="space-between" width="100%">
            <HStack>
              <Box w={3} h={3} bg="#ffc107" borderRadius="full" />
              <Text fontSize="sm">Neutral</Text>
            </HStack>
            <Text fontSize="sm" fontWeight="bold">
              {sentiment_distribution.neutral} ({neutralPercent}%)
            </Text>
          </HStack>
          <HStack justify="space-between" width="100%">
            <HStack>
              <Box w={3} h={3} bg="#dc3545" borderRadius="full" />
              <Text fontSize="sm">Negative</Text>
            </HStack>
            <Text fontSize="sm" fontWeight="bold">
              {sentiment_distribution.negative} ({negativePercent}%)
            </Text>
          </HStack>
        </VStack>

        {/* Top Topics */}
        <Box pt={4} borderTop="1px" borderColor="gray.100">
          <Text fontSize="md" fontWeight="semibold" mb={3}>
            Top Topics
          </Text>
          <VStack gap={2} align="stretch">
            {top_topics.slice(0, 5).map((topic, index) => (
              <HStack key={index} justify="space-between">
                <HStack>
                  <Text fontSize="sm" fontWeight="medium">
                    {topic.topic}
                  </Text>
                  <Badge
                    colorPalette={getSentimentColorPalette(topic.avg_sentiment)}
                    size="sm"
                  >
                    {topic.avg_sentiment}
                  </Badge>
                </HStack>
                <Text fontSize="sm" color="gray.500">
                  {topic.count}
                </Text>
              </HStack>
            ))}
          </VStack>
        </Box>
      </VStack>
    </Box>
  )
}
