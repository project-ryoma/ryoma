"use client"

import * as React from "react"
import { PopoverProps } from "@radix-ui/react-popover"
import { Check, ChevronsUpDown } from "lucide-react"

import { cn } from "@/lib/utils"
import { useMutationObserver } from "@/hooks/useMutationObserver"
import { Button } from "@/components/ui/button"
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command"
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "@/components/ui/hover-card"
import { Label } from "@/components/ui/label"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"

import { DataSource, DataSourceType } from "../../datasource/data/datasource"

interface DataSourceSelectorProps extends PopoverProps {
  types: readonly DataSourceType[]
  dataSources: DataSource[]
  selectedDataSource: DataSource
  peekedDataSource: DataSource
  onSelectDataSource: (dataSource: DataSource) => void
  onPeekDataSource: (dataSource: DataSource) => void
}

export function DataSourceSelector({
  dataSources,
  types,
  selectedDataSource,
  peekedDataSource,
  onSelectDataSource,
  ...props
}: DataSourceSelectorProps) {
  const [open, setOpen] = React.useState(false)

  const setPeekedDataSource = (dataSource: DataSource) => {
    props.onPeekDataSource(dataSource)
  }

  const setSelectedDataSource = (dataSource: DataSource) => {
    onSelectDataSource(dataSource)
  }

  return (
    <div className="grid gap-2">
      <HoverCard openDelay={200}>
        <HoverCardTrigger asChild>
          <Label htmlFor="dataSource">DataSource</Label>
        </HoverCardTrigger>
        <HoverCardContent
          align="start"
          className="w-[260px] text-sm"
          side="left"
        >
          The dataSource which will generate the completion. Some dataSources are suitable
          for natural language tasks, others specialize in code. Learn more.
        </HoverCardContent>
      </HoverCard>
      <Popover open={open} onOpenChange={setOpen} {...props}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            role="combobox"
            aria-expanded={open}
            aria-label="Select a dataSource"
            className="w-full justify-between"
          >
            {selectedDataSource ? selectedDataSource.name : "Select a dataSource..."}
            <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
          </Button>
        </PopoverTrigger>
        <PopoverContent align="end" className="w-[250px] p-0">
          <HoverCard>
            <Command loop>
              <CommandList className="h-[var(--cmdk-list-height)] max-h-[400px]">
                <CommandInput placeholder="Search DataSources..." />
                <CommandEmpty>No DataSources found.</CommandEmpty>
                <HoverCardTrigger />
                {types.map((type) => (
                  <CommandGroup key={type} heading={type}>
                    {dataSources
                      .filter((dataSource) => dataSource.type === type)
                      .map((dataSource) => (
                        <DataSourceItem
                          key={dataSource.id}
                          dataSource={dataSource}
                          isSelected={selectedDataSource?.id === dataSource.id}
                          onPeek={(dataSource) => setPeekedDataSource(dataSource)}
                          onSelect={() => {
                            setSelectedDataSource(dataSource)
                            setOpen(false)
                          }}
                        />
                      ))}
                  </CommandGroup>
                ))}
              </CommandList>
            </Command>
          </HoverCard>
        </PopoverContent>
      </Popover>
    </div>
  )
}

interface DataSourceItemProps {
  dataSource: DataSource
  isSelected: boolean
  onSelect: () => void
  onPeek: (dataSource: DataSource) => void
}

function DataSourceItem({ dataSource, isSelected, onSelect, onPeek }: DataSourceItemProps) {
  const ref = React.useRef<HTMLDivElement>(null)

  useMutationObserver(ref, (mutations) => {
    for (const mutation of mutations) {
      if (mutation.type === "attributes") {
        if (mutation.attributeName === "aria-selected") {
          onPeek(dataSource)
        }
      }
    }
  })

  return (
    <CommandItem
      key={dataSource.id}
      onSelect={onSelect}
      ref={ref}
      className="aria-selected:bg-primary aria-selected:text-primary-foreground"
    >
      {dataSource.name}
      <Check
        className={cn(
          "ml-auto h-4 w-4",
          isSelected ? "opacity-100" : "opacity-0"
        )}
      />
    </CommandItem>
  )
}
