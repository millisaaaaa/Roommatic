//import type { ChatKitOptions } from "@openai/chatkit";
/*
const options: ChatKitOptions = {
  api: {
    // TODO: configure your ChatKit API integration (URL, auth, uploads).
  },
  theme: {
    colorScheme: 'light',
    radius: 'pill',
    density: 'normal',
    typography: {
      baseSize: 16,
      fontFamily: '"OpenAI Sans", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif',
      fontFamilyMono: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "DejaVu Sans Mono", "Courier New", monospace',
      fontSources: [
        {
          family: 'OpenAI Sans',
          src: 'https://cdn.openai.com/common/fonts/openai-sans/v2/OpenAISans-Regular.woff2',
          weight: 400,
          style: 'normal',
          display: 'swap'
        }
      // ...and 7 more font sources
      ]
    }
  },
  composer: {
    placeholder: '問問Roomie',
    attachments: {
      enabled: true,
      maxCount: 5,
      maxSize: 10485760
    },
  },
  startScreen: {
    greeting: '你好，我是Roomie!'
  },
  // Optional fields not shown: locale, initialThread, threadItemActions, header, onClientTool, entities, widgets
};
*/

import { fileSearchTool, Agent, AgentInputItem, Runner, withTrace } from "@openai/agents";
import { z } from "zod";


// Tool definitions
const fileSearch = fileSearchTool([
  "vs_69ea01bdd5cc8191b243c7394cd4ba00"
])
const RoomieSchema = z.object({ paragraph: z.string() });
const roomie = new Agent({
  name: "Roomie",
  instructions: `You are Roomie, the AI assistant for Roomatic—a smart energy-saving and space management system. Your personality is playful and cute, and you are always eager to serve users with cheerfulness and warmth.

When users have difficulties using the system or want to understand energy-saving tips or details about their electricity usage, provide clear, friendly, and informative assistance in a lively and engaging manner. Guide users to effectively manage their energy consumption and space usage, ensuring your responses always reflect your playful and adorable assistant character.

# Output Format

Respond in concise, helpful paragraphs, using a playful and cute tone throughout your assistance.`,
  model: "gpt-4.1",
  tools: [
    fileSearch
  ],
  outputType: RoomieSchema,
  modelSettings: {
    temperature: 1,
    topP: 1,
    maxTokens: 2048,
    store: true
  }
});

type WorkflowInput = { input_as_text: string };


// Main code entrypoint
export const runWorkflow = async (workflow: WorkflowInput) => {
  return await withTrace("Roomie", async () => {
    const state = {

    };
    const conversationHistory: AgentInputItem[] = [
      { role: "user", content: [{ type: "input_text", text: workflow.input_as_text }] }
    ];
    const runner = new Runner({
      traceMetadata: {
        __trace_source__: "agent-builder",
        workflow_id: "wf_69e31333599c81909a1f031355008a59035422940b5929b6"
      }
    });
    const roomieResultTemp = await runner.run(
      roomie,
      [
        ...conversationHistory
      ]
    );
    conversationHistory.push(...roomieResultTemp.newItems.map((item) => item.rawItem));

    if (!roomieResultTemp.finalOutput) {
        throw new Error("Agent result is undefined");
    }
	/*
    const roomieResult = {
      output_text: JSON.stringify(roomieResultTemp.finalOutput),
      output_parsed: roomieResultTemp.finalOutput
    };
	*/
	return roomieResultTemp.finalOutput;
  });
}
