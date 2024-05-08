import { z } from "zod";

export const toolFormSchema = z.object({
  name: z.string(),
  arguments: z.record(z.string()),
});

export type ToolFormValues = z.infer<typeof toolFormSchema>;