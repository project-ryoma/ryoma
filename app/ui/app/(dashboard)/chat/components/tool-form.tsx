// build a chat confirmation form
// it has a message and two buttons to confirm or cancel
// the message is loaded as a prop

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { ToolInterface } from "./chat-board";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { useForm } from "react-hook-form";
import { useFieldArray } from "react-hook-form";
import exp from "constants";
import { type } from "os";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { use } from "react";
import { CodeEditor } from "./code-editor";
import { fi } from "date-fns/locale";
import { toolFormSchema, ToolFormValues } from "../data/tools";


type ToolFormProps = {
  tool: ToolInterface;
  onConfirm: (values: ToolFormValues) => Promise<void>;
  onCancel?: () => void;
};

const ToolForm = ({
  tool,
  onConfirm,
  onCancel = () => {},
}: ToolFormProps) => {

  const form = useForm<ToolFormValues>({
    resolver: zodResolver(toolFormSchema),
    defaultValues: {
      name: tool.name,
      arguments: tool.arguments
    } 
  });

  const handleConfirm = async (values: ToolFormValues) => {
    onConfirm(values);
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Kernel</CardTitle>
        <CardDescription>Confirm to run tool</CardDescription>
      </CardHeader>
      <CardContent className="grid gap-6">
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(handleConfirm)}
            className="space-y-2 w-full"
          >
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel htmlFor="tool_name">Tool name</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                </FormItem>
              )}
            />
            {Object.keys(tool.arguments).map((key) => {
              return (
                <FormField
                  key={key}
                  control={form.control}
                  name={`arguments.${key}`}
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel htmlFor={`tool_arguments_${key}`}>
                        {key}
                      </FormLabel>
                      <CodeEditor
                        value={field.value}
                        language="sql"
                        onChange={(value) => {
                        }}
                      />
                    </FormItem>
                  )}
                />
              );
            })} 
           
            <Button type="submit">Run</Button>
            <Button variant="secondary" onClick={onCancel}>
              Cancel
            </Button> 
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}

export default ToolForm;

