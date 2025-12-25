import Lake
open Lake DSL

package «LeanResearch» where
  -- add any package configuration options here

@[default_target]
lean_lib «LeanResearch» where
  -- add any library configuration options here

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git"
