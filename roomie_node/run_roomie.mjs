import { runWorkflow } from "./roomie.mjs";

const input = process.argv.slice(2).join(" ");

try {
  const result = await runWorkflow({ input_as_text: input });
  console.log(JSON.stringify(result));
} catch (err) {
  console.error(JSON.stringify({
    error: String(err?.message || err)
  }));
  process.exit(1);
}
