import { createFileRoute } from "@tanstack/react-router"
import { Box, Container, Heading } from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"

import AnalyticsDashboard from "@/components/Analytics/AnalyticsDashboard"
import { AnalyticsService } from "@/services/AnalyticsService"

export const Route = createFileRoute("/_layout/analytics")({
  component: Analytics,
})

function Analytics() {
  const { data: overviewData, isLoading: overviewLoading } = useQuery({
    queryKey: ["analytics", "overview"],
    queryFn: () => AnalyticsService.getAnalyticsOverview({ days: 30 }),
  })

  const { data: trendsData, isLoading: trendsLoading } = useQuery({
    queryKey: ["analytics", "trends"],
    queryFn: () => AnalyticsService.getResponseTrends({ days: 30 }),
  })

  const { data: sentimentData, isLoading: sentimentLoading } = useQuery({
    queryKey: ["analytics", "sentiment"],
    queryFn: () => AnalyticsService.getSentimentAnalysis({ days: 30 }),
  })

  const { data: performanceData, isLoading: performanceLoading } = useQuery({
    queryKey: ["analytics", "performance"],
    queryFn: () => AnalyticsService.getSurveyPerformance(),
  })

  const { data: recentFeedback, isLoading: recentLoading } = useQuery({
    queryKey: ["analytics", "recent"],
    queryFn: () => AnalyticsService.getRecentFeedback({ limit: 5 }),
  })

  const isLoading = overviewLoading || trendsLoading || sentimentLoading || performanceLoading || recentLoading

  return (
    <Container maxW="full" py={8}>
      <Box mb={8}>
        <Heading size="2xl" mb={2}>
          Analytics Dashboard
        </Heading>
        <Box color="gray.600" fontSize="lg">
          Survey performance insights and feedback analysis
        </Box>
      </Box>

      <AnalyticsDashboard
        overviewData={overviewData}
        trendsData={trendsData}
        sentimentData={sentimentData}
        performanceData={performanceData}
        recentFeedback={recentFeedback}
        isLoading={isLoading}
      />
    </Container>
  )
}
