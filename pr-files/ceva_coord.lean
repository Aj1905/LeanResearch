-- import Mathlib.Data.Real.Basic
-- import Mathlib.LinearAlgebra.LinearIndependent

-- noncomputable section

-- abbrev Pt := (ℝ × ℝ)

-- /-- 三点の非共線（(B-A) と (C-A) の一次独立で判定） -/
-- def nonCollinear (A B C : Pt) : Prop :=
--   LinearIndependent ℝ ![(B.1 - A.1, B.2 - A.2), (C.1 - A.1, C.2 - A.2)]

-- theorem Ceva
--   (A B C P : Pt)
--   (hABC : nonCollinear A B C)
--   (hABP : nonCollinear A B P)
--   (hACP : nonCollinear A C P)
--   (hBCP : nonCollinear B C P) :
--   -- D, E, F を辺 BC, CA, AB 上の点とし、P がセバー線 AD, BE, CF の交点であるとき
--   -- 有向比の積が 1 になる
--   ∃ (D E F : Pt) (u v w : ℝ),
--     D = (B.1 + u * (C.1 - B.1), B.2 + u * (C.2 - B.2)) ∧
--     E = (C.1 + v * (A.1 - C.1), C.2 + v * (A.2 - C.2)) ∧
--     F = (A.1 + w * (B.1 - A.1), A.2 + w * (B.2 - A.2)) ∧
--     (∃ (α β γ : ℝ),
--       P = (A.1 + α * (D.1 - A.1), A.2 + α * (D.2 - A.2)) ∧
--       P = (B.1 + β * (E.1 - B.1), B.2 + β * (E.2 - B.2)) ∧
--       P = (C.1 + γ * (F.1 - C.1), C.2 + γ * (F.2 - C.2))) →
--     (u / (1 - u)) * (v / (1 - v)) * (w / (1 - w)) = 1 := by



import Mathlib
import «affin_ratio»

noncomputable section

open scoped BigOperators
open Affine

namespace CevaCoord

/-- 座標空間としての平面。 -/
abbrev Pt := ℝ × ℝ

/-- `lineMap` を使った線分上の点のパラメータ表示。 -/
def pointOnSegment (A B : Pt) (t : ℝ) : Pt :=
  AffineMap.lineMap A B t

/-- R² 上のチェバの定理（順方向）.

三角形 `A B C` と、
`R` が `AB` 上、`P` が `BC` 上、`Q` が `CA` 上にあり、
`AP, BQ, CR` が一点で交わるとき、
`AR/RB * BP/PC * CQ/QA = 1` が成り立つ。

ここでは「比」を `affineRatio` で表現する。 -/
theorem ceva_coord
    (A B C P Q R : Pt)
    (hABC_noncol : ¬ AffineSubspace.collinear ℝ ({A, B, C} : Set Pt))
    (hP_on_BC : ∃ tP : ℝ, P = pointOnSegment B C tP)
    (hQ_on_CA : ∃ tQ : ℝ, Q = pointOnSegment C A tQ)
    (hR_on_AB : ∃ tR : ℝ, R = pointOnSegment A B tR)
    (h_concurrent :
      ∃ O : Pt,
        O ∈ AffineSubspace.line ℝ A P ∧
        O ∈ AffineSubspace.line ℝ B Q ∧
        O ∈ AffineSubspace.line ℝ C R) :
    Affine.affineRatio (k:=ℝ) A R B *
    Affine.affineRatio (k:=ℝ) B P C *
    Affine.affineRatio (k:=ℝ) C Q A = 1 :=
by
  classical
  -- スケッチ：
  -- 1. `hP_on_BC`, `hQ_on_CA`, `hR_on_AB` から、それぞれの点がどの t で表されるか取り出す。
  -- 2. `h_concurrent` から、共通点 O が `lineMap` で二通りずつ表されることを式にする。
  -- 3. R² なので vsub は単に (x,y) 引き算。座標ごとに式を分解する。
  -- 4. 連立一次方程式を解いて、`affineRatio` を t から表現し、積が 1 になることを field_simp 等で証明。
  --
  -- 実際に計算する部分はかなり長くなるので、実装時には
  -- 「純代数補題」を別ファイルに切って `ring` / `field_simp` で押し切るのがおすすめ。
  sorry

end CevaCoord
