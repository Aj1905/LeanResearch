import Lake
open Lake DSL

package «LeanResearch» where
  -- add any package configuration options here

@[default_target]
lean_lib PrFiles where
  -- PrFiles library

require mathlib from "../mathlib4"
