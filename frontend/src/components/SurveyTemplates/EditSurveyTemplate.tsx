// import {
//   Box,
//   Button,
//   FormControl,
//   FormErrorMessage,
//   FormLabel,
//   Input,
//   Modal,
//   ModalBody,
//   ModalCloseButton,
//   ModalContent,
//   ModalFooter,
//   ModalHeader,
//   ModalOverlay,
//   Switch,
//   Textarea,
//   VStack,
// } from "@chakra-ui/react"
// import { useMutation } from "@tanstack/react-query"
// import { type SubmitHandler, useForm } from "react-hook-form"
// import { useEffect, useState } from "react"

// import { SurveyTemplatesService } from "@/client"
// import type { SurveyTemplatePublic, SurveyTemplateUpdate } from "@/client"
// import useCustomToast from "@/hooks/useCustomToast"
// import QuestionBuilder from "./QuestionBuilder"

// interface EditSurveyTemplateProps {
//   surveyTemplate: SurveyTemplatePublic
//   open: boolean
//   onClose: () => void
//   onSurveyTemplateUpdated: () => void
// }

// interface SurveyTemplateFormData {
//   name: string
//   description: string
//   active: boolean
// }

// export default function EditSurveyTemplate({ 
//   surveyTemplate,
//   open, 
//   onClose, 
//   onSurveyTemplateUpdated 
// }: EditSurveyTemplateProps) {
//   const showToast = useCustomToast()
//   const [questions, setQuestions] = useState<Record<string, any>>(surveyTemplate.questions || {})
  
//   const {
//     register,
//     handleSubmit,
//     reset,
//     formState: { errors, isSubmitting },
//   } = useForm<SurveyTemplateFormData>({
//     mode: "onBlur",
//     criteriaMode: "all",
//     defaultValues: {
//       name: surveyTemplate.name,
//       description: surveyTemplate.description || "",
//       active: surveyTemplate.active,
//     },
//   })

//   // Reset form when surveyTemplate changes
//   useEffect(() => {
//     reset({
//       name: surveyTemplate.name,
//       description: surveyTemplate.description || "",
//       active: surveyTemplate.active,
//     })
//     setQuestions(surveyTemplate.questions || {})
//   }, [surveyTemplate, reset])

//   const mutation = useMutation({
//     mutationFn: (data: SurveyTemplateUpdate) => 
//       SurveyTemplatesService.updateSurveyTemplate({ 
//         surveyTemplateId: surveyTemplate.id, 
//         requestBody: data 
//       }),
//     onSuccess: () => {
//       showToast("Success", "Survey template updated successfully.", "success")
//       onSurveyTemplateUpdated()
//     },
//     onError: (err: any) => {
//       const errDetail = err.body?.detail || "Something went wrong."
//       showToast("Error", `Failed to update survey template: ${errDetail}`, "error")
//     },
//   })

//   const onSubmit: SubmitHandler<SurveyTemplateFormData> = async (data) => {
//     if (Object.keys(questions).length === 0) {
//       showToast("Error", "Please add at least one question to the survey template.", "error")
//       return
//     }

//     const surveyTemplateData: SurveyTemplateUpdate = {
//       name: data.name,
//       description: data.description || null,
//       active: data.active,
//       questions: questions,
//       triggers: surveyTemplate.triggers,
//       delivery_settings: surveyTemplate.delivery_settings,
//     }

//     mutation.mutate(surveyTemplateData)
//   }

//   const handleClose = () => {
//     reset()
//     setQuestions(surveyTemplate.questions || {})
//     onClose()
//   }

//   return (
//     <Modal isOpen={open} onClose={handleClose} size="4xl" scrollBehavior="inside">
//       <ModalOverlay />
//       <ModalContent>
//         <ModalHeader>Edit Survey Template</ModalHeader>
//         <ModalCloseButton />
        
//         <ModalBody>
//           <form onSubmit={handleSubmit(onSubmit)}>
//             <VStack spacing={6} align="stretch">
//               <FormControl isRequired isInvalid={!!errors.name}>
//                 <FormLabel htmlFor="name">Template Name</FormLabel>
//                 <Input
//                   id="name"
//                   {...register("name", {
//                     required: "Template name is required.",
//                     maxLength: {
//                       value: 255,
//                       message: "Template name must be 255 characters or less.",
//                     },
//                   })}
//                   placeholder="Enter template name"
//                 />
//                 {errors.name && (
//                   <FormErrorMessage>{errors.name.message}</FormErrorMessage>
//                 )}
//               </FormControl>

//               <FormControl>
//                 <FormLabel htmlFor="description">Description</FormLabel>
//                 <Textarea
//                   id="description"
//                   {...register("description")}
//                   placeholder="Enter template description (optional)"
//                   rows={3}
//                 />
//               </FormControl>

//               <FormControl>
//                 <FormLabel htmlFor="active">Active Template</FormLabel>
//                 <Switch
//                   id="active"
//                   {...register("active")}
//                   colorScheme="blue"
//                 />
//                 <Box fontSize="sm" color="gray.600" mt={1}>
//                   Active templates can be used to create feedback sessions
//                 </Box>
//               </FormControl>

//               <Box>
//                 <FormLabel>Survey Questions</FormLabel>
//                 <QuestionBuilder 
//                   questions={questions} 
//                   onChange={setQuestions} 
//                 />
//               </Box>
//             </VStack>
//           </form>
//         </ModalBody>

//         <ModalFooter>
//           <Button variant="ghost" mr={3} onClick={handleClose}>
//             Cancel
//           </Button>
//           <Button
//             colorScheme="blue"
//             onClick={handleSubmit(onSubmit)}
//             isLoading={isSubmitting || mutation.isPending}
//             loadingText="Updating..."
//           >
//             Update Template
//           </Button>
//         </ModalFooter>
//       </ModalContent>
//     </Modal>
//   )
// }
