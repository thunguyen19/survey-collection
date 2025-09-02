// import {
//   Box,
//   Button,
//   Card,
//   CardBody,
//   CardHeader,
//   Flex,
//   // FormControl,
//   // FormLabel,
//   HStack,
//   Icon,
//   IconButton,
//   Input,
//   Select,
//   Text,
//   Textarea,
//   VStack,
// } from "@chakra-ui/react"
// import { useState } from "react"
// import { FiPlus, FiTrash2, FiMoreVertical } from "react-icons/fi"

// interface Question {
//   id: string
//   type: "text" | "textarea" | "rating" | "multiple_choice" | "yes_no"
//   text: string
//   required: boolean
//   options?: string[]
//   min_rating?: number
//   max_rating?: number
// }

// interface QuestionBuilderProps {
//   questions: Record<string, any>
//   onChange: (questions: Record<string, any>) => void
// }

// const questionTypes = [
//   { value: "text", label: "Short Text" },
//   { value: "textarea", label: "Long Text" },
//   { value: "rating", label: "Rating Scale" },
//   { value: "multiple_choice", label: "Multiple Choice" },
//   { value: "yes_no", label: "Yes/No" },
// ]

// export default function QuestionBuilder({ questions, onChange }: QuestionBuilderProps) {
//   const questionList = Object.entries(questions).map(([id, question]) => ({
//     id,
//     ...question
//   })) as Question[]

//   const addQuestion = () => {
//     const newId = `q_${Date.now()}`
//     const newQuestion: Question = {
//       id: newId,
//       type: "text",
//       text: "",
//       required: false,
//     }
    
//     const updatedQuestions = {
//       ...questions,
//       [newId]: newQuestion,
//     }
//     onChange(updatedQuestions)
//   }

//   const updateQuestion = (id: string, updates: Partial<Question>) => {
//     const updatedQuestions = {
//       ...questions,
//       [id]: { ...questions[id], ...updates },
//     }
//     onChange(updatedQuestions)
//   }

//   const deleteQuestion = (id: string) => {
//     const updatedQuestions = { ...questions }
//     delete updatedQuestions[id]
//     onChange(updatedQuestions)
//   }

//   const addOption = (questionId: string) => {
//     const question = questions[questionId]
//     const options = question.options || []
//     updateQuestion(questionId, {
//       options: [...options, ""],
//     })
//   }

//   const updateOption = (questionId: string, optionIndex: number, value: string) => {
//     const question = questions[questionId]
//     const options = [...(question.options || [])]
//     options[optionIndex] = value
//     updateQuestion(questionId, { options })
//   }

//   const deleteOption = (questionId: string, optionIndex: number) => {
//     const question = questions[questionId]
//     const options = [...(question.options || [])]
//     options.splice(optionIndex, 1)
//     updateQuestion(questionId, { options })
//   }

//   return <div>Placeholder</div>

//   // return (
//   //   <VStack spacing={4} align="stretch">
//   //     {questionList.map((question, index) => (
//   //       <Card key={question.id} variant="outline">
//   //         <CardHeader pb={2}>
//   //           <Flex justify="space-between" align="center">
//   //             <HStack>
//   //               <Icon as={FiMoreVertical} color="gray.400" />
//   //               <Text fontWeight="medium" fontSize="sm" color="gray.600">
//   //                 Question {index + 1}
//   //               </Text>
//   //             </HStack>
//   //             <IconButton
//   //               icon={<Icon as={FiTrash2} />}
//   //               size="sm"
//   //               variant="ghost"
//   //               colorScheme="red"
//   //               onClick={() => deleteQuestion(question.id)}
//   //               aria-label="Delete question"
//   //             />
//   //           </Flex>
//   //         </CardHeader>
          
//   //         <CardBody pt={0}>
//   //           <VStack spacing={4} align="stretch">
//   //             <HStack spacing={4} align="start">
//   //               <FormControl flex={2}>
//   //                 <FormLabel fontSize="sm">Question Text</FormLabel>
//   //                 <Textarea
//   //                   value={question.text}
//   //                   onChange={(e) => updateQuestion(question.id, { text: e.target.value })}
//   //                   placeholder="Enter your question"
//   //                   size="sm"
//   //                   rows={2}
//   //                 />
//   //               </FormControl>
                
//   //               <FormControl flex={1}>
//   //                 <FormLabel fontSize="sm">Question Type</FormLabel>
//   //                 <Select
//   //                   value={question.type}
//   //                   onChange={(e) => updateQuestion(question.id, { 
//   //                     type: e.target.value as Question["type"],
//   //                     // Reset type-specific fields when changing type
//   //                     options: e.target.value === "multiple_choice" ? [""] : undefined,
//   //                     min_rating: e.target.value === "rating" ? 1 : undefined,
//   //                     max_rating: e.target.value === "rating" ? 5 : undefined,
//   //                   })}
//   //                   size="sm"
//   //                 >
//   //                   {questionTypes.map((type) => (
//   //                     <option key={type.value} value={type.value}>
//   //                       {type.label}
//   //                     </option>
//   //                   ))}
//   //                 </Select>
//   //               </FormControl>
//   //             </HStack>

//   //             {/* Rating Scale Options */}
//   //             {question.type === "rating" && (
//   //               <HStack>
//   //                 <FormControl>
//   //                   <FormLabel fontSize="sm">Min Rating</FormLabel>
//   //                   <Input
//   //                     type="number"
//   //                     size="sm"
//   //                     value={question.min_rating || 1}
//   //                     onChange={(e) => updateQuestion(question.id, { 
//   //                       min_rating: parseInt(e.target.value) || 1 
//   //                     })}
//   //                     min={1}
//   //                     max={10}
//   //                   />
//   //                 </FormControl>
//   //                 <FormControl>
//   //                   <FormLabel fontSize="sm">Max Rating</FormLabel>
//   //                   <Input
//   //                     type="number"
//   //                     size="sm"
//   //                     value={question.max_rating || 5}
//   //                     onChange={(e) => updateQuestion(question.id, { 
//   //                       max_rating: parseInt(e.target.value) || 5 
//   //                     })}
//   //                     min={1}
//   //                     max={10}
//   //                   />
//   //                 </FormControl>
//   //               </HStack>
//   //             )}

//   //             {/* Multiple Choice Options */}
//   //             {question.type === "multiple_choice" && (
//   //               <Box>
//   //                 <FormLabel fontSize="sm">Options</FormLabel>
//   //                 <VStack spacing={2} align="stretch">
//   //                   {(question.options || []).map((option: string, optionIndex: number) => (
//   //                     <HStack key={optionIndex}>
//   //                       <Input
//   //                         size="sm"
//   //                         value={option}
//   //                         onChange={(e) => updateOption(question.id, optionIndex, e.target.value)}
//   //                         placeholder={`Option ${optionIndex + 1}`}
//   //                       />
//   //                       <IconButton
//   //                         icon={<Icon as={FiTrash2} />}
//   //                         size="sm"
//   //                         variant="ghost"
//   //                         colorScheme="red"
//   //                         onClick={() => deleteOption(question.id, optionIndex)}
//   //                         aria-label="Delete option"
//   //                       />
//   //                     </HStack>
//   //                   ))}
//   //                   <Button
//   //                     size="sm"
//   //                     variant="ghost"
//   //                     leftIcon={<Icon as={FiPlus} />}
//   //                     onClick={() => addOption(question.id)}
//   //                     alignSelf="flex-start"
//   //                   >
//   //                     Add Option
//   //                   </Button>
//   //                 </VStack>
//   //               </Box>
//   //             )}

//   //             {/* Required Toggle */}
//   //             <FormControl>
//   //               <label>
//   //                 <input
//   //                   type="checkbox"
//   //                   checked={question.required}
//   //                   onChange={(e) => updateQuestion(question.id, { required: e.target.checked })}
//   //                 />
//   //                 <Text as="span" fontSize="sm" ml={2}>
//   //                   Required question
//   //                 </Text>
//   //               </label>
//   //             </FormControl>
//   //           </VStack>
//   //         </CardBody>
//   //       </Card>
//   //     ))}

//   //     <Button
//   //       leftIcon={<Icon as={FiPlus} />}
//   //       onClick={addQuestion}
//   //       variant="outline"
//   //       colorScheme="blue"
//   //       size="lg"
//   //     >
//   //       Add Question
//   //     </Button>

//   //     {questionList.length === 0 && (
//   //       <Box textAlign="center" py={8} color="gray.500">
//   //         <Text>No questions added yet. Click "Add Question" to get started.</Text>
//   //       </Box>
//   //     )}
//   //   </VStack>
//   // )
// }
