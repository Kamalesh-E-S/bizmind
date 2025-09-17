import { remark } from "remark"
import html from "remark-html"

/**
 * Converts Markdown to HTML string.
 * @param markdown - Markdown content to convert.
 * @returns HTML string.
 */
export default async function markdownToHtml(markdown: string): Promise<string> {
  const result = await remark().use(html).process(markdown)
  return result.toString()
}
