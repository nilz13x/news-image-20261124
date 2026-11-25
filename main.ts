// News Image 24 Nov: the front page is the entry.png beside this file.
// The program copies it byte for byte to the grader's output directory,
// so both runs write identical bytes. No network, no drawing at run time.
// The copy is checked: if the written file is not the same size as the
// source, the run fails loudly instead of submitting a broken entry.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, statSync } from "node:fs";
import { join } from "node:path";

const src = new URL("./entry.png", import.meta.url);
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(outDir, { recursive: true });
const dest = join(outDir, "entry.png");
copyFileSync(src, dest);
if (statSync(dest).size !== statSync(src).size) {
  throw new Error("entry.png copy is incomplete");
}
