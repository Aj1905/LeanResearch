import Mathlib

noncomputable section

open scoped BigOperators

namespace Affine

variable {k V P : Type*}
variable [Field k] [AddCommGroup V] [Module k V] [AffineSpace V P]

/-- 3点 `A B C` に対する「アフィン比」（biratio）.

`B -ᵥ A = r • (C -ᵥ A)` を満たす `r : k` が一意に存在するならその `r`、
そうでなければ `0` と定義する。

幾何的には、3点が一直線上にあり `A ≠ C` のときに
有向距離比 `AB/AC`（をベクトル比で表したもの）になっている。 -/
noncomputable def affineRatio (A B C : P) : k :=
by
  classical
  by_cases h : ∃! r : k, B -ᵥ A = r • (C -ᵥ A)
  · exact Classical.some h
  · exact 0

lemma affineRatio_def_pos {A B C : P}
    (h : ∃! r : k, B -ᵥ A = r • (C -ᵥ A)) :
    affineRatio (k:=k) A B C = Classical.some h :=
by
  classical
  unfold affineRatio
  simp [h]

/-- `affineRatio` の特徴付け：
一意解が存在する状況では、`B -ᵥ A = affineRatio A B C • (C -ᵥ A)` が成り立つ。 -/
lemma affineRatio_spec {A B C : P}
    (h : ∃! r : k, B -ᵥ A = r • (C -ᵥ A)) :
    B -ᵥ A = affineRatio (k:=k) A B C • (C -ᵥ A) :=
by
  classical
  have : affineRatio (k:=k) A B C = Classical.some h :=
    affineRatio_def_pos (k:=k) (A:=A) (B:=B) (C:=C) h
  -- `Classical.some_spec h` : B -ᵥ A = (Classical.some h) • (C -ᵥ A)
  simpa [this] using (Classical.some_spec h)

/-- collinear かつ `A ≠ C` なら、`affineRatio A B C` は一意な `r` で与えられる。

実際の mathlib PR では、`collinear` API を使ってこの補題をきれいに書く。 -/
lemma affineRatio_exists_unique_of_collinear
    {A B C : P}
    (h_col : AffineSubspace.collinear k ({A, B, C} : Set P))
    (hAC : A ≠ C) :
    ∃! r : k, B -ᵥ A = r • (C -ᵥ A) :=
by
  classical
  -- スケッチ：
  -- 1. collinear から `B -ᵥ A` と `C -ᵥ A` が一次従属 / 比例関係にあることを取り出す
  -- 2. `A ≠ C` から `C -ᵥ A ≠ 0` を得る
  -- 3. 一次元部分空間上での一意性で `∃! r` を構成する
  sorry

/-- collinear で `A ≠ C` のとき、`affineRatio` は 0 ではないときも多いが、
`B = A` なら当然 0 になる、などの基本事実をここに集める。

実際の PR では、`collinear` API に合わせて細かい補題をいくつかに分ける。 -/
lemma affineRatio_A_self_C (A C : P) :
    affineRatio (k:=k) A A C = 0 :=
by
  classical
  -- `B = A` なら `B -ᵥ A = 0` なので、`r = 0` も解。
  -- しかし一意でない可能性もあるので default として 0 は自然。
  unfold affineRatio
  by_cases h : ∃! r : k, A -ᵥ A = r • (C -ᵥ A)
  · -- この場合でも some h = 0 になることを示す補題を別途立ててもよい
    -- 今回はスケッチなので `sorry`
    sorry
  · simp [h]

end Affine
