"use client";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { DataSource } from "../data/datasource";
import { useForm } from "react-hook-form";
import * as z from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { DataSourceCard } from "./data-source-card";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area"

const formSchema = z.object({
  user: z.string(),
  password: z.string(),
  host: z.string(),
  port: z.number(),
  database: z.string(),
  schema: z.string(),
  type: z.string(),
  role: z.string(),
});

type DataSourceFormValues = z.infer<typeof formSchema>;

interface DataSourceModalProps {
  dataSources: DataSource[];
  isOpen: boolean;
  onClose: () => void;
}

export function DataSourceModal({ dataSources, isOpen, onClose}: DataSourceModalProps) {
  const form = useForm<DataSourceFormValues>({
    resolver: zodResolver(formSchema),
  });

  const onSubmit = (values: DataSourceFormValues) => {
    // handle the form submission
  }

  return (
    <Modal
      title="Create and Connect to a Data Source"
      isOpen={isOpen}
      description=""
      onClose={onClose}
    >
      <div className="flex flex-col">
      <ScrollArea className="w-96 whitespace-nowrap rounded-md" >
        <div className="flex space-x-4 p-4">
          {dataSources?.map((dataSource) => (
            <DataSourceCard
              key={dataSource.id}
              dataSource={dataSource}
              onClick={() => {}}
            />
          ))}
        </div>
        <ScrollBar orientation="horizontal" />
      </ScrollArea>
      <Form {...form}>
        <form className="space-y-4">
          {Object.keys(formSchema.shape).map((key) => {
            // get the key as the name of the field
            const k = key as keyof DataSourceFormValues;
            return (
              <FormField
                key={key}
                control={form.control}
                name={k}
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>{key}</FormLabel>
                    <FormControl>
                      <Input
                        {...field}
                        type={key === "password" ? "password" : "text"}
                      />
                    </FormControl>
                  </FormItem>
                )}
              />
            );
          })}


        </form>
      </Form>
      <div className="pt-6 space-x-2 flex items-center justify-end w-full">
        <Button onClick={() => onSubmit(form.getValues())}>Connect</Button> 
        <Button variant="outline" onClick={onClose}>
          Cancel
        </Button>
      </div>
      </div>
    </Modal>
  );
}

