import { Badge, Container, Flex, Heading, Table, Text } from "@chakra-ui/react"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { z } from "zod"

import { type UserPublic } from "@/client"
// TODO: OrganizationsService will be available after regenerating the API client
import { OrganizationsService } from "@/client"
import AddOrganization from "@/components/Organizations/AddOrganization"
import { OrganizationActionsMenu } from "@/components/Organizations/OrganizationActionsMenu"
import PendingOrganizations from "@/components/Pending/PendingOrganizations"
import {
  PaginationItems,
  PaginationNextTrigger,
  PaginationPrevTrigger,
  PaginationRoot,
} from "@/components/ui/pagination.tsx"

const organizationsSearchSchema = z.object({
  page: z.number().catch(1),
})

const PER_PAGE = 5

function getOrganizationsQueryOptions({ page }: { page: number }) {
  return {
    queryFn: async () => {
      // TODO: Replace with actual OrganizationsService call after regenerating API client
      return OrganizationsService.readOrganizations({ skip: (page - 1) * PER_PAGE, limit: PER_PAGE })
      
      // Mock data for now
      // return {
      //   data: [
      //     {
      //       id: "1",
      //       name: "General Hospital",
      //       type: "hospital",
      //       subscription_tier: "premium",
      //       active: true,
      //       created_at: new Date().toISOString(),
      //       updated_at: new Date().toISOString(),
      //     },
      //     {
      //       id: "2", 
      //       name: "City Clinic",
      //       type: "clinic",
      //       subscription_tier: "basic",
      //       active: true,
      //       created_at: new Date().toISOString(),
      //       updated_at: new Date().toISOString(),
      //     }
      //   ],
      //   count: 2
      // }
    },
    queryKey: ["organizations", { page }],
  }
}

export const Route = createFileRoute("/_layout/organizations")({
  component: Organizations,
  validateSearch: (search) => organizationsSearchSchema.parse(search),
})

function OrganizationsTable() {
  const queryClient = useQueryClient()
  const currentUser = queryClient.getQueryData<UserPublic>(["currentUser"])
  const navigate = useNavigate({ from: Route.fullPath })
  const { page } = Route.useSearch()

  const { data, isLoading, isPlaceholderData } = useQuery({
    ...getOrganizationsQueryOptions({ page }),
    placeholderData: (prevData) => prevData,
  })

  const setPage = (page: number) =>
    navigate({
      search: (prev: { [key: string]: string }) => ({ ...prev, page }),
    })

  const organizations = data?.data.slice(0, PER_PAGE) ?? []
  const count = data?.count ?? 0

  if (isLoading) {
    return <PendingOrganizations />
  }

  return (
    <>
      <Table.Root size={{ base: "sm", md: "md" }}>
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeader w="sm">Name</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Type</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Subscription</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Status</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Actions</Table.ColumnHeader>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {organizations?.map((org) => (
            <Table.Row key={org.id} opacity={isPlaceholderData ? 0.5 : 1}>
              <Table.Cell>
                {org.name}
                {currentUser?.organization_id === org.id && (
                  <Badge ml="1" colorScheme="teal">
                    Your Org
                  </Badge>
                )}
              </Table.Cell>
              <Table.Cell color={!org.type ? "gray" : "inherit"}>
                {org.type || "N/A"}
              </Table.Cell>
              <Table.Cell>
                {org.subscription_tier || "basic"}
              </Table.Cell>
              <Table.Cell>{org.active ? "Active" : "Inactive"}</Table.Cell>
              <Table.Cell>
                {currentUser?.is_superuser ? (
                  <OrganizationActionsMenu
                    organization={org}
                    disabled={false}
                  />
                ) : (
                  <Text color="gray.500" fontSize="sm">
                    View Only
                  </Text>
                )}
              </Table.Cell>
            </Table.Row>
          ))}
        </Table.Body>
      </Table.Root>
      <Flex justifyContent="flex-end" mt={4}>
        <PaginationRoot
          count={count}
          pageSize={PER_PAGE}
          onPageChange={({ page }) => setPage(page)}
        >
          <Flex>
            <PaginationPrevTrigger />
            <PaginationItems />
            <PaginationNextTrigger />
          </Flex>
        </PaginationRoot>
      </Flex>
    </>
  )
}

function Organizations() {
  const queryClient = useQueryClient()
  const currentUser = queryClient.getQueryData<UserPublic>(["currentUser"])

  return (
    <Container maxW="full">
      <Heading size="lg" pt={12}>
        Organizations Management
      </Heading>
      
      {/* <Text color="orange.500" fontSize="sm" mb={4} p={3} bg="orange.50" borderRadius="md">
        📝 Note: This page uses mock data. To connect to the real API, regenerate the API client after the backend organizations routes are deployed.
      </Text> */}

      {currentUser?.is_superuser && <AddOrganization />}
      <OrganizationsTable />
    </Container>
  )
}
