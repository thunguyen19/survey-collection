import {
  Box,
  Button,
  HStack,
  Input,
  Text,
  Textarea,
  VStack,
} from "@chakra-ui/react"
import { useState } from "react"
import { FiPlus, FiTrash2 } from "react-icons/fi"
import { useMutation, useQueryClient } from "@tanstack/react-query"

import { SurveyTemplatesService } from "@/client"
import type { SurveyTemplatePublic, SurveyTemplateUpdate } from "@/client"
import useCustomToast from "@/hooks/useCustomToast"
import {
  DialogActionTrigger,
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog"

interface Question {
  id: string
  type: "text" | "textarea" | "rating" | "multiple_choice" | "yes_no"
  text: string
  required: boolean
  options?: string[]
  min_rating?: number
  max_rating?: number
}

interface ManageQuestionsProps {
  template: SurveyTemplatePublic
}

const questionTypes = [
  { value: "text", label: "Short Text" },
  { value: "textarea", label: "Long Text" },
  { value: "rating", label: "Rating Scale" },
  { value: "multiple_choice", label: "Multiple Choice" },
  { value: "yes_no", label: "Yes/No" },
]

export default function ManageQuestions({ template }: ManageQuestionsProps) {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [isOpen, setIsOpen] = useState(false)
  
  // Convert template.questions to Question array
  const [questions, setQuestions] = useState<Question[]>(() => {
    if (!template.questions || typeof template.questions !== 'object') return []
    return Object.entries(template.questions).map(([id, question]: [string, any]) => ({
      id,
      type: question.type || "text",
      text: question.text || "",
      required: question.required || false,
      options: question.options || [],
      min_rating: question.min_rating || 1,
      max_rating: question.max_rating || 5,
    }))
  })

  const updateMutation = useMutation({
    mutationFn: (updateData: SurveyTemplateUpdate) => 
      SurveyTemplatesService.updateSurveyTemplate({
        surveyTemplateId: template.id,
        requestBody: updateData,
      }),
    onSuccess: () => {
      showSuccessToast("Questions updated successfully.")
      queryClient.invalidateQueries({ queryKey: ["survey-templates"] })
      setIsOpen(false)
    },
    onError: () => {
      showErrorToast("Failed to update questions.")
    },
  })

  const addQuestion = () => {
    const newQuestion: Question = {
      id: `question_${Date.now()}`,
      type: "text",
      text: "",
      required: false,
    }
    setQuestions([...questions, newQuestion])
  }

  const updateQuestion = (id: string, field: keyof Question, value: any) => {
    setQuestions(questions.map(q => 
      q.id === id ? { ...q, [field]: value } : q
    ))
  }

  const removeQuestion = (id: string) => {
    setQuestions(questions.filter(q => q.id !== id))
  }

  const handleSave = () => {
    // Convert questions array back to Record<string, any> format
    const questionsRecord: Record<string, any> = {}
    questions.forEach(q => {
      const { id, ...questionData } = q
      questionsRecord[id] = questionData
    })

    const updateData: SurveyTemplateUpdate = {
      questions: questionsRecord,
    }

    updateMutation.mutate(updateData)
  }

  const getQuestionCount = () => questions.length

  return (
    <DialogRoot
      open={isOpen}
      onOpenChange={({ open }) => setIsOpen(open)}
    >
      <DialogTrigger asChild>
        <Button size="sm" variant="outline" style={{ color: "#006496" }}> 
          Manage Questions ({getQuestionCount()})
        </Button>
      </DialogTrigger>

      <DialogContent>
        <DialogHeader>
          <DialogTitle>Manage Questions - {template.name}</DialogTitle>
        </DialogHeader>

        <DialogBody>
          <VStack gap={4} align="stretch" maxHeight="400px" overflowY="auto">
            {questions.length === 0 ? (
              <Text color="gray.500" textAlign="center" py={4}>
                No questions added yet. Click "Add Question" to get started.
              </Text>
            ) : (
              questions.map((question) => (
                <Box key={question.id} p={4} borderWidth={1} borderRadius="md" bg="gray.50">
                  <VStack gap={3} align="stretch">
                    <HStack justify="space-between">
                      <select
                        value={question.type}
                        onChange={(e: React.ChangeEvent<HTMLSelectElement>) => updateQuestion(question.id, "type", e.target.value)}
                        style={{
                          width: "200px",
                          padding: "8px",
                          borderRadius: "6px",
                          border: "1px solid #E2E8F0",
                          backgroundColor: "white"
                        }}
                      >
                        {questionTypes.map((type) => (
                          <option key={type.value} value={type.value}>
                            {type.label}
                          </option>
                        ))}
                      </select>
                      <Button
                        size="sm"
                        variant="outline"
                        colorPalette="red"
                        onClick={() => removeQuestion(question.id)}
                      >
                        <FiTrash2 />
                      </Button>
                    </HStack>

                    <Textarea
                      placeholder="Enter your question..."
                      value={question.text}
                      onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => updateQuestion(question.id, "text", e.target.value)}
                      rows={2}
                    />

                    <HStack>
                      <label>
                        <input
                          type="checkbox"
                          checked={question.required}
                          onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateQuestion(question.id, "required", e.target.checked)}
                        />
                        <Text as="span" ml={2} fontSize="sm">
                          Required
                        </Text>
                      </label>
                    </HStack>

                    {question.type === "rating" && (
                      <HStack>
                        <Text fontSize="sm">Rating Scale:</Text>
                        <Input
                          type="number"
                          min={1}
                          max={10}
                          value={question.min_rating}
                          onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateQuestion(question.id, "min_rating", parseInt(e.target.value))}
                          width="80px"
                        />
                        <Text fontSize="sm">to</Text>
                        <Input
                          type="number"
                          min={1}
                          max={10}
                          value={question.max_rating}
                          onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateQuestion(question.id, "max_rating", parseInt(e.target.value))}
                          width="80px"
                        />
                      </HStack>
                    )}

                    {question.type === "multiple_choice" && (
                      <VStack align="stretch" gap={2}>
                        <Text fontSize="sm" fontWeight="medium">Options:</Text>
                        {(question.options || []).map((option, index) => (
                          <HStack key={index}>
                            <Input
                              value={option}
                              onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                                const newOptions = [...(question.options || [])]
                                newOptions[index] = e.target.value
                                updateQuestion(question.id, "options", newOptions)
                              }}
                              placeholder={`Option ${index + 1}`}
                            />
                            <Button
                              size="sm"
                              variant="outline"
                              colorPalette="red"
                              onClick={() => {
                                const newOptions = (question.options || []).filter((_, i) => i !== index)
                                updateQuestion(question.id, "options", newOptions)
                              }}
                            >
                              <FiTrash2 />
                            </Button>
                          </HStack>
                        ))}
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            const newOptions = [...(question.options || []), ""]
                            updateQuestion(question.id, "options", newOptions)
                          }}
                        >
                          <FiPlus /> Add Option
                        </Button>
                      </VStack>
                    )}
                  </VStack>
                </Box>
              ))
            )}

            <Button onClick={addQuestion} variant="outline" colorPalette="#006496">
              <FiPlus /> Add Question
            </Button>
          </VStack>
        </DialogBody>

        <DialogFooter>
          <DialogActionTrigger asChild>
            <Button variant="outline" color="#006496">Cancel</Button>
          </DialogActionTrigger>
          <Button
            onClick={handleSave}
            loading={updateMutation.isPending}
            backgroundColor="#006496"
          >
            Save Questions
          </Button>
        </DialogFooter>

        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  )
}
