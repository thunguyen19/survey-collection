import {
  Box,
  Heading,
  Text,
  VStack,
  HStack,
} from "@chakra-ui/react"

interface TrendData {
  trends: Array<{
    date: string
    surveys_sent: number
    responses_received: number
    response_rate: number
  }>
  summary: {
    total_surveys: number
    total_responses: number
    avg_response_rate: number
  }
}

interface ResponseTrendsChartProps {
  data?: TrendData
}

export default function ResponseTrendsChart({ data }: ResponseTrendsChartProps) {
  if (!data) {
    return null
  }

  // Simple SVG chart implementation
  const chartWidth = 600
  const chartHeight = 250
  const padding = 40

  const maxSurveys = Math.max(...data.trends.map(t => t.surveys_sent))
  const maxResponses = Math.max(...data.trends.map(t => t.responses_received))
  const maxValue = Math.max(maxSurveys, maxResponses)

  // Create points for the lines
  const surveyPoints = data.trends.map((trend, index) => {
    const x = padding + (index / (data.trends.length - 1)) * (chartWidth - 2 * padding)
    const y = chartHeight - padding - (trend.surveys_sent / maxValue) * (chartHeight - 2 * padding)
    return `${x},${y}`
  }).join(' ')

  const responsePoints = data.trends.map((trend, index) => {
    const x = padding + (index / (data.trends.length - 1)) * (chartWidth - 2 * padding)
    const y = chartHeight - padding - (trend.responses_received / maxValue) * (chartHeight - 2 * padding)
    return `${x},${y}`
  }).join(' ')

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
            Response Trends
          </Heading>
          <Text color="gray.600" fontSize="sm">
            Survey delivery and response patterns over the last 30 days
          </Text>
        </Box>

        {/* Chart Container */}
        <Box position="relative" width="100%" height="300px" overflow="hidden">
          <svg
            width="100%"
            height="100%"
            viewBox={`0 0 ${chartWidth} ${chartHeight}`}
            style={{ maxWidth: '100%', height: 'auto' }}
          >
            {/* Grid lines */}
            {[0, 0.25, 0.5, 0.75, 1].map((ratio) => {
              const y = chartHeight - padding - ratio * (chartHeight - 2 * padding)
              return (
                <line
                  key={ratio}
                  x1={padding}
                  y1={y}
                  x2={chartWidth - padding}
                  y2={y}
                  stroke="#f0f0f0"
                  strokeWidth="1"
                />
              )
            })}

            {/* Y-axis labels */}
            {[0, 0.25, 0.5, 0.75, 1].map((ratio) => {
              const y = chartHeight - padding - ratio * (chartHeight - 2 * padding)
              const value = Math.round(maxValue * ratio)
              return (
                <text
                  key={ratio}
                  x={padding - 10}
                  y={y + 5}
                  textAnchor="end"
                  fontSize="12"
                  fill="#666"
                >
                  {value}
                </text>
              )
            })}

            {/* Surveys sent line */}
            <polyline
              points={surveyPoints}
              fill="none"
              stroke="#006496"
              strokeWidth="3"
              strokeLinecap="round"
              strokeLinejoin="round"
            />

            {/* Responses received line */}
            <polyline
              points={responsePoints}
              fill="none"
              stroke="#28a745"
              strokeWidth="3"
              strokeLinecap="round"
              strokeLinejoin="round"
            />

            {/* Data points */}
            {data.trends.map((trend, index) => {
              const x = padding + (index / (data.trends.length - 1)) * (chartWidth - 2 * padding)
              const surveyY = chartHeight - padding - (trend.surveys_sent / maxValue) * (chartHeight - 2 * padding)
              const responseY = chartHeight - padding - (trend.responses_received / maxValue) * (chartHeight - 2 * padding)
              
              return (
                <g key={index}>
                  <circle cx={x} cy={surveyY} r="4" fill="#006496" />
                  <circle cx={x} cy={responseY} r="4" fill="#28a745" />
                </g>
              )
            })}
          </svg>
        </Box>

        {/* Legend */}
        <HStack justify="center" gap={6}>
          <HStack>
            <Box w={3} h={3} bg="#006496" borderRadius="full" />
            <Text fontSize="sm" color="gray.600">
              Surveys Sent ({data.summary.total_surveys})
            </Text>
          </HStack>
          <HStack>
            <Box w={3} h={3} bg="#28a745" borderRadius="full" />
            <Text fontSize="sm" color="gray.600">
              Responses ({data.summary.total_responses})
            </Text>
          </HStack>
        </HStack>

        {/* Summary Stats */}
        <HStack justify="space-around" pt={4} borderTop="1px" borderColor="gray.100">
          <VStack gap={1}>
            <Text fontSize="2xl" fontWeight="bold" color="gray.800">
              {data.summary.avg_response_rate}%
            </Text>
            <Text fontSize="sm" color="gray.500">
              Avg Response Rate
            </Text>
          </VStack>
          <VStack gap={1}>
            <Text fontSize="2xl" fontWeight="bold" color="gray.800">
              {data.summary.total_surveys}
            </Text>
            <Text fontSize="sm" color="gray.500">
              Total Surveys
            </Text>
          </VStack>
          <VStack gap={1}>
            <Text fontSize="2xl" fontWeight="bold" color="gray.800">
              {data.summary.total_responses}
            </Text>
            <Text fontSize="sm" color="gray.500">
              Total Responses
            </Text>
          </VStack>
        </HStack>
      </VStack>
    </Box>
  )
}
