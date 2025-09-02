import {
  Box,
  Grid,
  GridItem,
  Skeleton,
  VStack,
} from "@chakra-ui/react"

import MetricsOverview from "@/components/Analytics/MetricsOverview"
import ResponseTrendsChart from "@/components/Analytics/ResponseTrendsChart"
import SentimentAnalysis from "@/components/Analytics/SentimentAnalysis"
import SurveyPerformance from "@/components/Analytics/SurveyPerformance"
import RecentFeedback from "@/components/Analytics/RecentFeedback"

interface AnalyticsDashboardProps {
  overviewData?: any
  trendsData?: any
  sentimentData?: any
  performanceData?: any
  recentFeedback?: any
  isLoading: boolean
}

export default function AnalyticsDashboard({
  overviewData,
  trendsData,
  sentimentData,
  performanceData,
  recentFeedback,
  isLoading,
}: AnalyticsDashboardProps) {
  if (isLoading) {
    return (
      <VStack gap={6} align="stretch">
        {/* Overview Cards Skeleton */}
        <Grid templateColumns="repeat(auto-fit, minmax(250px, 1fr))" gap={6}>
          {Array.from({ length: 4 }).map((_, i) => (
            <GridItem key={i}>
              <Box p={6} bg="white" borderRadius="lg" shadow="sm" borderWidth={1}>
                <Skeleton height="20px" width="60%" mb={4} />
                <Skeleton height="32px" width="40%" mb={2} />
                <Skeleton height="16px" width="80%" />
              </Box>
            </GridItem>
          ))}
        </Grid>

        {/* Charts Skeleton */}
        <Grid templateColumns={{ base: "1fr", lg: "2fr 1fr" }} gap={6}>
          <GridItem>
            <Box p={6} bg="white" borderRadius="lg" shadow="sm" borderWidth={1}>
              <Skeleton height="20px" width="40%" mb={4} />
              <Skeleton height="300px" />
            </Box>
          </GridItem>
          <GridItem>
            <Box p={6} bg="white" borderRadius="lg" shadow="sm" borderWidth={1}>
              <Skeleton height="20px" width="50%" mb={4} />
              <Skeleton height="300px" />
            </Box>
          </GridItem>
        </Grid>

        {/* Additional content skeleton */}
        <Grid templateColumns={{ base: "1fr", lg: "1fr 1fr" }} gap={6}>
          <GridItem>
            <Box p={6} bg="white" borderRadius="lg" shadow="sm" borderWidth={1}>
              <Skeleton height="20px" width="60%" mb={4} />
              <Skeleton height="200px" />
            </Box>
          </GridItem>
          <GridItem>
            <Box p={6} bg="white" borderRadius="lg" shadow="sm" borderWidth={1}>
              <Skeleton height="20px" width="50%" mb={4} />
              <Skeleton height="200px" />
            </Box>
          </GridItem>
        </Grid>
      </VStack>
    )
  }

  return (
    <VStack gap={6} align="stretch">
      {/* Overview Metrics */}
      <MetricsOverview data={overviewData} />

      {/* Charts Row */}
      <Grid templateColumns={{ base: "1fr", lg: "2fr 1fr" }} gap={6}>
        <GridItem>
          <ResponseTrendsChart data={trendsData} />
        </GridItem>
        <GridItem>
          <SentimentAnalysis data={sentimentData} />
        </GridItem>
      </Grid>

      {/* Bottom Row */}
      <Grid templateColumns={{ base: "1fr", lg: "1fr 1fr" }} gap={6}>
        <GridItem>
          <SurveyPerformance data={performanceData} />
        </GridItem>
        <GridItem>
          <RecentFeedback data={recentFeedback} />
        </GridItem>
      </Grid>
    </VStack>
  )
}
