import Mathlib
import «affin_ratio»
import «CevaCoord»

noncomputable section

open scoped BigOperators
open Affine

namespace Ceva

variable {k V P : Type*}
variable [Field k] [AddCommGroup V] [Module k V] [AffineSpace V P]

/-- 三角形 `A B C` の「辺上の点」条件を、`AffineSubspace` ベースで書いたもの。 -/
structure OnTriangleSides (A B C P Q R : P) : Prop :=
  (P_on_BC : P ∈ AffineSubspace.line k B C)
  (Q_on_CA : Q ∈ AffineSubspace.line k C A)
  (R_on_AB : R ∈ AffineSubspace.line k A B)

/-- Ceva の「共点性」条件。 -/
def concurrent (A B C P Q R : P) : Prop :=
  ∃ O : P,
    O ∈ AffineSubspace.line k A P ∧
    O ∈ AffineSubspace.line k B Q ∧
    O ∈ AffineSubspace.line k C R

/-- 一般アフィン空間におけるチェバの定理（順方向）の型。

実際の定理は `h_on_sides` と `h_concurrent` を仮定して、
`affineRatio` の積が 1 であることを結論とする。 -/
theorem ceva
    (A B C P Q R : P)
    (hABC_affine_indep : AffineIndependent k ![A, B, C])
    (h_on_sides : OnTriangleSides (k:=k) A B C P Q R)
    (h_concurrent : concurrent (k:=k) A B C P Q R) :
    Affine.affineRatio (k:=k) A R B *
    Affine.affineRatio (k:=k) B P C *
    Affine.affineRatio (k:=k) C Q A = 1 :=
by
  classical
  -- 方針：
  -- 1. `Y : AffineSubspace V P := affineSpan k ({A,B,C} : Set P)` を取る。
  -- 2. `hABC_affine_indep` から `Y` が 2 次元であることを示す。
  -- 3. 「2 次元アフィン空間は `k × k` とアフィン同型」が mathlib にあればそれを使って
  --    `φ : Y ≃ᵃ[k] (k × k)` を取る。
  -- 4. `φ` を使って `A B C P Q R` を R² 上の点 `A' B' C' P' Q' R'` に移す。
  -- 5. `OnTriangleSides` と `concurrent` が `φ` で保たれることを示す補題を使う：
  --    - `φ` は直線を直線に送る
  --    - `affineRatio` も `φ` で不変（線形部分が同型だから比も保存）
  -- 6. `CevaCoord.ceva_coord` を R² 上の点に適用し、比の積 = 1 を得る。
  -- 7. 比の積が `affineRatio` で保存されているので、そのまま元の空間での結論になる。
  --
  -- 実際には、(2)(3) に対応する「アフィン同型の存在」と
  -- (5) に対応する「アフィン同型がアフィン比と共点性を保存する」という補題を
  -- 別ファイルで証明する必要がある。
  sorry

end Ceva
