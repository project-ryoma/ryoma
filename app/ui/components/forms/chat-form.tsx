"use client";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { ChevronUpIcon } from "@radix-ui/react-icons"
import { Input } from "@/components/ui/input";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";


const formSchema = z.object({
  question: z.string(),
})

type ChatFormValue = z.infer<typeof formSchema>;
type ChatFormProps = {
  onSubmit: (values: ChatFormValue, uniqueIdToRetry?: string | null) => Promise<void>;
  loading?: boolean;
};

export default function ChatForm({ onSubmit, loading }: ChatFormProps) {
  const form = useForm<ChatFormValue>({
    resolver: zodResolver(formSchema),
  });


  // Function to handle form submission
  const handleSubmit = async (values: ChatFormValue) => {
    onSubmit(values); // Call the onSubmit passed via props
  };


  return (
    <>
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(handleSubmit)}
          className="space-y-2 w-full"
        >
          <FormField
            control={form.control}
            name="question"
            render={({ field }) => (
              <FormItem className="flex items-center space-x-2">
                  <FormLabel />
                  <FormControl>
                    <Input
                      type="question"
                      placeholder="Ask your data..."
                      disabled={loading}
                      className="flex-grow"
                      {...field}
                      />
                  </FormControl>
                  <Button variant="outline" size="icon" type="submit">
                    <ChevronUpIcon className="h-4 w-4" />
                  </Button>
                  <FormMessage />
              </FormItem>
            )}
          />
        </form>
      </Form>

    </>
  );
}
