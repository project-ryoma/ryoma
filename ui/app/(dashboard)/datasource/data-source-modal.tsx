"use client";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { DataSource } from "./data/datasource";
import { useForm } from "react-hook-form";
import * as z from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

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
  dataSource: DataSource;
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (values: DataSourceFormValues) => void;
}

export function DataSourceModal({ dataSource, isOpen, onClose, onSubmit }: DataSourceModalProps) {
  const form = useForm<DataSourceFormValues>({
    resolver: zodResolver(formSchema),
  });


  return (
    <Modal
      title={dataSource.name}
      isOpen={isOpen}
      description={dataSource.description || ""}
      onClose={onClose}
    >
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
    </Modal>
  );
}

