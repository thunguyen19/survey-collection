import {
  Box,
  Grid,
  GridItem,
  Heading,
  Text,
  VStack,
  HStack,
  Icon,
} from "@chakra-ui/react"
import { FiSend, FiMessageCircle, FiTrendingUp, FiClock } from "react-icons/fi"

interface MetricCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon: any
  color: string
}

function MetricCard({ title, value, subtitle, icon, color }: MetricCardProps) {
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
      <HStack justify="space-between" mb={4}>
        <Text fontSize="sm" color="gray.600" fontWeight="medium">
          {title}
        </Text>
        <Icon as={icon} color={color} boxSize={5} />
      </HStack>
      <VStack align="start" gap={1}>
        <Heading size="2xl" color="gray.800">
          {value}
        </Heading>
        {subtitle && (
          <Text fontSize="sm" color="gray.500">
            {subtitle}
          </Text>
        )}
      </VStack>
    </Box>
  )
}

interface MetricsOverviewProps {
  data?: {
    total_surveys_sent: number
    total_responses: number
    response_rate: number
    active_templates: number
    avg_completion_time: number
  }
}

export default function MetricsOverview({ data }: MetricsOverviewProps) {
  if (!data) {
    return null
  }

  const metrics = [
    {
      title: "Surveys Sent",
      value: data.total_surveys_sent.toLocaleString(),
      subtitle: "Last 30 days",
      icon: FiSend,
      color: "#006496",
    },
    {
      title: "Responses Received",
      value: data.total_responses.toLocaleString(),
      subtitle: "Last 30 days",
      icon: FiMessageCircle,
      color: "#28a745",
    },
    {
      title: "Response Rate",
      value: `${data.response_rate}%`,
      subtitle: "Average completion rate",
      icon: FiTrendingUp,
      color: "#ffc107",
    },
    {
      title: "Avg. Completion Time",
      value: `${data.avg_completion_time} min`,
      subtitle: `${data.active_templates} active templates`,
      icon: FiClock,
      color: "#17a2b8",
    },
  ]

  return (
    <Grid templateColumns="repeat(auto-fit, minmax(250px, 1fr))" gap={6}>
      {metrics.map((metric, index) => (
        <GridItem key={index}>
          <MetricCard {...metric} />
        </GridItem>
      ))}
    </Grid>
  )
}
