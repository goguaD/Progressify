from app.models import Meal


def meal_out_dict(meal: Meal, my_rating: float | None = None) -> dict:
    rc = meal.rating_count or 0
    avg = round(meal.rating_sum / rc, 1) if rc > 0 else 0.0
    avg = round(avg * 2) / 2

    return {
        "id": meal.id,
        "name": meal.name,
        "name_ka": meal.name_ka,
        "description": meal.description,
        "description_ka": meal.description_ka,
        "image_url": meal.image_url,
        "goal": meal.goal,
        "calories": meal.calories,
        "protein": meal.protein,
        "carbs": meal.carbs,
        "fat": meal.fat,
        "fiber": meal.fiber,
        "sugar": meal.sugar,
        "views": meal.views,
        "rating": avg,
        "rating_count": rc,
        "my_rating": my_rating,
        "added_by": meal.added_by,
        "added_by_username": (
            meal.author.username if meal.author else None
        ),
        "is_default": meal.is_default,
        "created_at": meal.created_at,
    }


DEFAULT_MEALS: list[dict] = [
    # ── CUT / FAT LOSS ───────────────────────────────────────────
    {
        "name": "Grilled Chicken Breast with Steamed Broccoli",
        "description": (
            "Serves 1 | Prep: 10 min | Cook: 20 min\n\n"
            "Ingredients:\n"
            "• 200 g boneless, skinless chicken breast (1 medium piece)\n"
            "• 1 tsp olive oil\n"
            "• 1 clove garlic, minced\n"
            "• ½ tsp smoked paprika\n"
            "• Juice of ½ lemon\n"
            "• Salt & black pepper to taste\n"
            "• 200 g broccoli florets (about 2 cups)\n"
            "• 1 tsp low-sodium soy sauce\n"
            "• ½ tsp sesame oil\n\n"
            "Instructions:\n"
            "1. Butterfly the chicken breast so it is even thickness (about 1.5 cm). "
            "Rub with olive oil, minced garlic, paprika, lemon juice, salt and pepper. "
            "Let it marinate for at least 5 minutes.\n"
            "2. Preheat a grill pan or outdoor grill to medium-high heat (around 200 °C / 400 °F). "
            "Grill the chicken for 5–6 minutes per side until the internal temperature reaches "
            "74 °C (165 °F). Let it rest for 3 minutes before slicing.\n"
            "3. While the chicken grills, bring a pot of water to a boil. Steam the broccoli florets "
            "in a steamer basket for 4–5 minutes until bright green and tender-crisp.\n"
            "4. Toss the steamed broccoli with soy sauce and sesame oil.\n"
            "5. Plate the sliced chicken alongside the broccoli and serve immediately."
        ),
        "image_url": "https://images.unsplash.com/photo-1532550907401-a500c9a57435?w=600",
        "goal": "cut",
        "calories": 350,
        "protein": 42.0,
        "carbs": 12.0,
        "fat": 8.0,
        "fiber": 4.0,
        "sugar": 3.0,
    },
    {
        "name": "Tuna Poke Bowl",
        "description": (
            "Serves 1 | Prep: 15 min | Cook: 5 min (cauliflower rice)\n\n"
            "Ingredients:\n"
            "• 150 g sushi-grade ahi tuna, cut into 1.5 cm cubes\n"
            "• 1 tbsp low-sodium soy sauce\n"
            "• 1 tsp sesame oil\n"
            "• ½ tsp rice vinegar\n"
            "• 150 g riced cauliflower (fresh or frozen)\n"
            "• 50 g cucumber, diced\n"
            "• 40 g shelled edamame\n"
            "• 1 tbsp pickled ginger\n"
            "• 1 tsp furikake seasoning\n"
            "• Optional: thin slices of nori, sesame seeds\n\n"
            "Instructions:\n"
            "1. In a bowl, combine the tuna cubes with soy sauce, sesame oil and rice vinegar. "
            "Toss gently and refrigerate for 10 minutes.\n"
            "2. Heat a non-stick pan over medium heat. Add the cauliflower rice and cook for "
            "3–4 minutes, stirring occasionally, until just tender. Season with a pinch of salt.\n"
            "3. Place the cauliflower rice in a wide bowl. Arrange the marinated tuna, cucumber, "
            "edamame and pickled ginger on top.\n"
            "4. Sprinkle with furikake and sesame seeds. Serve immediately — do not cook the tuna."
        ),
        "image_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=600",
        "goal": "cut",
        "calories": 380,
        "protein": 38.0,
        "carbs": 22.0,
        "fat": 12.0,
        "fiber": 5.0,
        "sugar": 4.0,
    },
    {
        "name": "Egg White Veggie Omelette",
        "description": (
            "Serves 1 | Prep: 5 min | Cook: 8 min\n\n"
            "Ingredients:\n"
            "• 6 large egg whites (about 180 ml)\n"
            "• 30 g fresh spinach\n"
            "• 40 g white mushrooms, sliced\n"
            "• 30 g red bell pepper, diced\n"
            "• 20 g feta cheese, crumbled\n"
            "• 1 tsp olive oil or cooking spray\n"
            "• Salt & pepper to taste\n"
            "• 6–8 cherry tomatoes for serving\n\n"
            "Instructions:\n"
            "1. Whisk the egg whites with a pinch of salt and pepper until slightly frothy.\n"
            "2. Heat olive oil in a 24 cm (10-inch) non-stick skillet over medium heat. "
            "Sauté the mushrooms and bell pepper for 2–3 minutes until softened. "
            "Add the spinach and cook for 30 seconds until wilted. Transfer veggies to a plate.\n"
            "3. Wipe the pan, add a tiny bit more oil and pour in the egg whites. "
            "Tilt the pan to spread evenly. Cook undisturbed for 2 minutes until the edges set.\n"
            "4. Scatter the sautéed vegetables and feta over one half of the omelette. "
            "Fold the other half over and cook for another 1–2 minutes.\n"
            "5. Slide onto a plate, halve the cherry tomatoes alongside, and serve."
        ),
        "image_url": "https://images.unsplash.com/photo-1525351484163-7529414344d8?w=600",
        "goal": "cut",
        "calories": 280,
        "protein": 32.0,
        "carbs": 10.0,
        "fat": 9.0,
        "fiber": 3.0,
        "sugar": 4.0,
    },
    {
        "name": "Greek Yogurt Protein Bowl",
        "description": (
            "Serves 1 | Prep: 5 min | No cooking required\n\n"
            "Ingredients:\n"
            "• 200 g Greek yogurt (0% fat)\n"
            "• 60 g mixed berries (blueberries, raspberries, strawberries)\n"
            "• 1 tbsp honey (about 15 g)\n"
            "• 1 tbsp chia seeds (10 g)\n"
            "• 15 g raw almonds (about 10 almonds)\n"
            "• Optional: a few fresh mint leaves\n\n"
            "Instructions:\n"
            "1. Spoon the Greek yogurt into a bowl.\n"
            "2. Rinse the berries. If using strawberries, hull and halve them.\n"
            "3. Arrange the berries on top of the yogurt. Drizzle with honey.\n"
            "4. Sprinkle chia seeds and almonds over the top.\n"
            "5. For best texture, let it sit for 2–3 minutes so the chia seeds begin to swell, "
            "then eat immediately. You can also prep this the night before in a jar — "
            "refrigerate overnight and the chia seeds will create a pudding-like consistency."
        ),
        "image_url": "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=600",
        "goal": "cut",
        "calories": 310,
        "protein": 30.0,
        "carbs": 35.0,
        "fat": 7.0,
        "fiber": 6.0,
        "sugar": 18.0,
    },
    {
        "name": "Shrimp Stir-Fry with Zucchini Noodles",
        "description": (
            "Serves 1 | Prep: 10 min | Cook: 8 min\n\n"
            "Ingredients:\n"
            "• 180 g jumbo shrimp, peeled and deveined (about 10 pieces)\n"
            "• 2 medium zucchini (about 300 g), spiralized into noodles\n"
            "• 2 cloves garlic, minced\n"
            "• 1 tsp fresh ginger, finely grated\n"
            "• ¼ tsp red chili flakes\n"
            "• 1 tsp olive oil\n"
            "• Juice of ½ lime\n"
            "• 1 tsp low-sodium soy sauce\n"
            "• Salt to taste\n\n"
            "Instructions:\n"
            "1. Pat the shrimp dry with paper towels and season lightly with salt.\n"
            "2. Heat olive oil in a large skillet or wok over high heat until it shimmers. "
            "Add the shrimp in a single layer and sear for 1.5 minutes per side until pink "
            "and opaque. Remove to a plate.\n"
            "3. In the same pan, add the garlic, ginger and chili flakes. "
            "Stir for 30 seconds until fragrant (reduce heat if garlic browns too fast).\n"
            "4. Add the zucchini noodles. Toss for 2–3 minutes over high heat — you want them "
            "warmed through but still slightly firm, not mushy.\n"
            "5. Return the shrimp to the pan. Add soy sauce and lime juice, "
            "toss everything together for 30 seconds and serve immediately."
        ),
        "image_url": "https://images.unsplash.com/photo-1563379926898-05f4575a45d8?w=600",
        "goal": "cut",
        "calories": 290,
        "protein": 34.0,
        "carbs": 14.0,
        "fat": 10.0,
        "fiber": 3.0,
        "sugar": 6.0,
    },

    # ── BULK / MUSCLE GAIN ───────────────────────────────────────
    {
        "name": "Double Chicken Burrito Bowl",
        "description": (
            "Serves 1 | Prep: 15 min | Cook: 25 min\n\n"
            "Ingredients:\n"
            "• 250 g boneless chicken thighs, cut into 2 cm pieces\n"
            "• 1 tsp cumin, ½ tsp chili powder, ½ tsp garlic powder, salt & pepper\n"
            "• 1 tsp olive oil\n"
            "• 120 g white rice (dry weight — yields ~300 g cooked)\n"
            "• Juice of ½ lime + 1 tbsp chopped cilantro (for the rice)\n"
            "• 80 g canned black beans, drained and rinsed\n"
            "• 50 g roasted corn (canned or frozen, pan-charred)\n"
            "• 40 g guacamole (about 2 tbsp)\n"
            "• 30 g salsa\n"
            "• 1 tbsp sour cream\n\n"
            "Instructions:\n"
            "1. Cook the rice according to package directions (typically 1:2 rice-to-water ratio, "
            "simmer covered for 15 min). Once done, fluff with a fork and stir in lime juice and "
            "cilantro.\n"
            "2. Toss the chicken pieces with cumin, chili powder, garlic powder, salt and pepper.\n"
            "3. Heat olive oil in a large skillet over medium-high heat. Cook the chicken for "
            "6–8 minutes, turning occasionally, until browned and cooked through (internal "
            "temp 74 °C / 165 °F).\n"
            "4. Warm the black beans in a small saucepan or microwave (1 min). "
            "Pan-char the corn in a dry hot skillet for 2 minutes.\n"
            "5. Assemble: place the cilantro-lime rice in a bowl, top with chicken, black beans, "
            "corn, guacamole, salsa and sour cream."
        ),
        "image_url": "https://images.unsplash.com/photo-1623428187969-5da2dcea5ebf?w=600",
        "goal": "bulk",
        "calories": 720,
        "protein": 55.0,
        "carbs": 68.0,
        "fat": 24.0,
        "fiber": 10.0,
        "sugar": 5.0,
    },
    {
        "name": "Beef & Sweet Potato Power Plate",
        "description": (
            "Serves 1 | Prep: 10 min | Cook: 30 min\n\n"
            "Ingredients:\n"
            "• 200 g lean ground beef (90/10)\n"
            "• 1 medium sweet potato (about 200 g), peeled and cut into 2 cm cubes\n"
            "• 150 g green beans, trimmed\n"
            "• ½ medium onion, diced\n"
            "• 2 cloves garlic, minced\n"
            "• 1 tsp olive oil\n"
            "• Salt, pepper, ½ tsp smoked paprika\n\n"
            "Instructions:\n"
            "1. Preheat oven to 200 °C (400 °F). Toss sweet potato cubes with ½ tsp olive oil, "
            "salt and paprika. Spread on a lined baking sheet in a single layer. "
            "Roast for 22–25 minutes, flipping halfway, until golden and fork-tender.\n"
            "2. While the sweet potato roasts, heat ½ tsp olive oil in a large skillet over "
            "medium-high heat. Sauté the onion for 3 minutes, then add garlic and cook "
            "30 seconds more.\n"
            "3. Add the ground beef, break it up with a spatula, and cook for 6–7 minutes until "
            "browned and no pink remains. Season with salt and pepper. Drain any excess fat.\n"
            "4. Steam or boil the green beans for 4–5 minutes until tender-crisp.\n"
            "5. Plate the beef, sweet potato and green beans side by side. Serve hot."
        ),
        "image_url": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=600",
        "goal": "bulk",
        "calories": 650,
        "protein": 48.0,
        "carbs": 55.0,
        "fat": 22.0,
        "fiber": 7.0,
        "sugar": 12.0,
    },
    {
        "name": "Salmon & Quinoa Bowl",
        "description": (
            "Serves 1 | Prep: 10 min | Cook: 25 min\n\n"
            "Ingredients:\n"
            "• 180 g Atlantic salmon fillet (skin-on or skinless)\n"
            "• 1 tbsp Dijon mustard + 1 tsp honey (glaze)\n"
            "• 80 g quinoa (dry weight — yields ~200 g cooked)\n"
            "• 100 g asparagus spears (about 6 spears), trimmed\n"
            "• 1 tsp olive oil\n"
            "• Juice of ½ lemon\n"
            "• Salt & pepper to taste\n\n"
            "Instructions:\n"
            "1. Preheat oven to 200 °C (400 °F). Line a small baking sheet with parchment.\n"
            "2. Rinse quinoa in a fine mesh strainer. Combine with 160 ml water and a pinch of "
            "salt in a saucepan. Bring to a boil, reduce to low, cover and simmer 15 minutes. "
            "Remove from heat, keep covered 5 minutes, then fluff with a fork.\n"
            "3. Place the salmon on the baking sheet. Mix mustard and honey, brush over the top. "
            "Season with salt and pepper.\n"
            "4. Toss asparagus with olive oil and salt, arrange around the salmon on the sheet.\n"
            "5. Bake for 12–15 minutes until the salmon flakes easily and registers "
            "52 °C (125 °F) internally for medium.\n"
            "6. Plate the quinoa, lay the salmon on top, arrange asparagus alongside, "
            "and finish with a squeeze of fresh lemon."
        ),
        "image_url": "https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=600",
        "goal": "bulk",
        "calories": 680,
        "protein": 46.0,
        "carbs": 52.0,
        "fat": 28.0,
        "fiber": 6.0,
        "sugar": 8.0,
    },
    {
        "name": "Peanut Butter Banana Protein Shake",
        "description": (
            "Serves 1 | Prep: 5 min | No cooking required\n\n"
            "Ingredients:\n"
            "• 300 ml whole milk\n"
            "• 2 scoops (60 g) whey protein powder (vanilla or chocolate)\n"
            "• 1 ripe banana (about 120 g)\n"
            "• 2 tbsp natural peanut butter (32 g)\n"
            "• 30 g rolled oats\n"
            "• 3–4 ice cubes\n"
            "• Optional: 1 tsp honey, pinch of cinnamon\n\n"
            "Instructions:\n"
            "1. Add the oats to a blender and pulse a few times to break them down into a "
            "rough flour — this makes the shake smoother.\n"
            "2. Add the milk, protein powder, banana (broken into chunks), peanut butter "
            "and ice cubes.\n"
            "3. Blend on high for 45–60 seconds until completely smooth and frothy.\n"
            "4. Pour into a large glass or shaker cup. The shake is quite thick — "
            "if you prefer thinner consistency, add 50 ml more milk.\n"
            "5. Drink within 30 minutes of making for best taste and texture. "
            "Ideal post-workout or as a mid-morning snack when bulking."
        ),
        "image_url": "https://images.unsplash.com/photo-1553787499-6f9133860278?w=600",
        "goal": "bulk",
        "calories": 620,
        "protein": 52.0,
        "carbs": 58.0,
        "fat": 22.0,
        "fiber": 5.0,
        "sugar": 28.0,
    },
    {
        "name": "Pasta with Turkey Meatballs",
        "description": (
            "Serves 1 | Prep: 15 min | Cook: 25 min\n\n"
            "Ingredients:\n"
            "• 100 g whole-wheat penne (dry weight)\n"
            "• 200 g lean ground turkey\n"
            "• 1 clove garlic, minced\n"
            "• 1 tbsp breadcrumbs\n"
            "• 1 tsp dried oregano, ½ tsp dried basil\n"
            "• 1 egg white\n"
            "• Salt & pepper\n"
            "• 150 ml marinara sauce (store-bought or homemade)\n"
            "• 15 g grated parmesan\n\n"
            "Instructions:\n"
            "1. In a bowl, combine the ground turkey, garlic, breadcrumbs, oregano, basil, "
            "egg white, salt and pepper. Mix with your hands until just combined — "
            "don't overwork. Roll into 5–6 meatballs (about 35 g each).\n"
            "2. Heat a non-stick skillet over medium heat with a light spray of oil. "
            "Sear the meatballs for 2–3 minutes per side until browned on all sides.\n"
            "3. Pour the marinara sauce into the pan, reduce heat to low, cover and simmer "
            "for 12–15 minutes until meatballs are cooked through (internal temp 74 °C / 165 °F).\n"
            "4. Meanwhile, cook the penne in a large pot of salted boiling water according to "
            "package directions (usually 10–12 min). Drain, reserving 2 tbsp pasta water.\n"
            "5. Toss the pasta with the meatballs and sauce, adding a splash of pasta water "
            "to loosen if needed. Top with grated parmesan and serve."
        ),
        "image_url": "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=600",
        "goal": "bulk",
        "calories": 700,
        "protein": 45.0,
        "carbs": 78.0,
        "fat": 18.0,
        "fiber": 8.0,
        "sugar": 10.0,
    },

    # ── MAINTAIN ─────────────────────────────────────────────────
    {
        "name": "Mediterranean Chicken Wrap",
        "description": (
            "Serves 1 | Prep: 10 min | Cook: 10 min\n\n"
            "Ingredients:\n"
            "• 150 g boneless chicken breast, sliced into thin strips\n"
            "• 1 large whole-wheat tortilla (about 60 g)\n"
            "• 2 tbsp hummus (30 g)\n"
            "• 30 g mixed greens (arugula, spinach)\n"
            "• 4–5 sun-dried tomatoes, chopped\n"
            "• 2 thin slices red onion\n"
            "• 20 g feta cheese, crumbled\n"
            "• ½ tsp olive oil\n"
            "• ½ tsp dried oregano, salt & pepper\n\n"
            "Instructions:\n"
            "1. Season the chicken strips with oregano, salt and pepper. "
            "Heat olive oil in a skillet over medium-high heat and cook the chicken for "
            "4–5 minutes per side until golden and cooked through.\n"
            "2. Warm the tortilla in a dry pan for 20 seconds per side or in the microwave "
            "for 10 seconds.\n"
            "3. Spread hummus down the center of the tortilla. Layer on the mixed greens, "
            "cooked chicken, sun-dried tomatoes, red onion and feta.\n"
            "4. Fold the bottom edge up, then roll the sides in tightly to form a wrap. "
            "Cut in half diagonally and serve. Wraps well in foil for meal prep."
        ),
        "image_url": "https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=600",
        "goal": "maintain",
        "calories": 480,
        "protein": 36.0,
        "carbs": 42.0,
        "fat": 16.0,
        "fiber": 6.0,
        "sugar": 5.0,
    },
    {
        "name": "Teriyaki Salmon Rice Bowl",
        "description": (
            "Serves 1 | Prep: 10 min | Cook: 20 min\n\n"
            "Ingredients:\n"
            "• 150 g salmon fillet\n"
            "• 2 tbsp teriyaki sauce (store-bought or: 1 tbsp soy sauce + 1 tsp honey + "
            "½ tsp rice vinegar + ½ tsp cornstarch)\n"
            "• 100 g jasmine rice (dry — yields ~250 g cooked)\n"
            "• 100 g baby bok choy, halved lengthwise\n"
            "• 50 g carrots, julienned\n"
            "• 1 tsp sesame seeds\n"
            "• 1 tsp vegetable oil\n\n"
            "Instructions:\n"
            "1. Cook jasmine rice: rinse, combine with 150 ml water, bring to a boil, "
            "reduce to low, cover and simmer 12 minutes. Rest covered 5 minutes.\n"
            "2. Pat the salmon dry. Brush with half the teriyaki sauce.\n"
            "3. Heat oil in a non-stick skillet over medium-high heat. Place the salmon "
            "skin-side up and sear for 3 minutes. Flip and cook 3–4 minutes more "
            "until it flakes easily. Brush with remaining teriyaki in the last minute.\n"
            "4. In the same pan, quickly stir-fry bok choy and carrots for 2 minutes "
            "over high heat.\n"
            "5. Assemble: rice in a bowl, salmon on top (break into chunks or leave whole), "
            "vegetables on the side. Sprinkle with sesame seeds."
        ),
        "image_url": "https://images.unsplash.com/photo-1512058564366-18510be2db19?w=600",
        "goal": "maintain",
        "calories": 520,
        "protein": 38.0,
        "carbs": 48.0,
        "fat": 18.0,
        "fiber": 4.0,
        "sugar": 10.0,
    },
    {
        "name": "Turkey & Avocado Sandwich",
        "description": (
            "Serves 1 | Prep: 5 min | No cooking required\n\n"
            "Ingredients:\n"
            "• 2 slices sourdough bread (about 70 g total)\n"
            "• 120 g sliced roast turkey breast (deli-style or home-roasted)\n"
            "• ½ ripe avocado (about 60 g), sliced\n"
            "• 2 slices ripe tomato\n"
            "• 2–3 leaves of butter lettuce\n"
            "• 1 tsp Dijon mustard\n"
            "• Salt & pepper to taste\n\n"
            "Instructions:\n"
            "1. Toast the sourdough slices until golden (toaster or dry skillet, "
            "2 minutes per side).\n"
            "2. Spread Dijon mustard on one slice.\n"
            "3. Layer the turkey, avocado slices, tomato and lettuce on top. "
            "Season with a pinch of salt and pepper.\n"
            "4. Close with the second slice, press gently, and cut in half diagonally.\n"
            "5. Best eaten fresh. For meal prep, store the avocado separately and add just "
            "before eating to prevent browning."
        ),
        "image_url": "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=600",
        "goal": "maintain",
        "calories": 470,
        "protein": 34.0,
        "carbs": 38.0,
        "fat": 18.0,
        "fiber": 7.0,
        "sugar": 4.0,
    },
    {
        "name": "Grilled Steak Salad",
        "description": (
            "Serves 1 | Prep: 10 min | Cook: 12 min\n\n"
            "Ingredients:\n"
            "• 180 g sirloin steak (about 2 cm thick)\n"
            "• 80 g mixed salad greens\n"
            "• 8 cherry tomatoes, halved\n"
            "• 2 thin slices red onion\n"
            "• 25 g blue cheese, crumbled\n"
            "• 1 tbsp balsamic vinegar + 1 tsp olive oil + ½ tsp Dijon (dressing)\n"
            "• Salt & pepper\n\n"
            "Instructions:\n"
            "1. Remove the steak from the fridge 20 minutes before cooking. "
            "Pat dry and season generously with salt and pepper on both sides.\n"
            "2. Heat a cast-iron skillet or grill pan over high heat until smoking. "
            "Sear the steak for 3–4 minutes per side for medium-rare (internal temp "
            "55 °C / 130 °F). For medium, cook 4–5 minutes per side (60 °C / 140 °F).\n"
            "3. Rest the steak on a cutting board for 5 minutes, then slice against the grain "
            "into 1 cm strips.\n"
            "4. While the steak rests, whisk together balsamic vinegar, olive oil and Dijon "
            "to make the dressing.\n"
            "5. Arrange the greens on a plate, top with tomatoes, red onion and steak slices. "
            "Scatter blue cheese and drizzle with dressing."
        ),
        "image_url": "https://images.unsplash.com/photo-1546793665-c74683f339c1?w=600",
        "goal": "maintain",
        "calories": 500,
        "protein": 40.0,
        "carbs": 15.0,
        "fat": 28.0,
        "fiber": 4.0,
        "sugar": 6.0,
    },

    # ── Cheat Meals (healthier alternatives) ─────────────────

    {
        "name": "High-Protein Chocolate Mug Cake",
        "description": (
            "Serves 1 | Prep: 3 min | Cook: 2 min (microwave)\n\n"
            "Ingredients:\n"
            "• 1 scoop (30 g) chocolate whey protein powder\n"
            "• 1 tbsp cocoa powder (unsweetened)\n"
            "• 1 large egg\n"
            "• 2 tbsp unsweetened applesauce (30 g)\n"
            "• 1 tbsp almond flour (7 g)\n"
            "• ½ tsp baking powder\n"
            "• Pinch of salt\n"
            "• Optional: 10 g dark chocolate chips, 1 tsp honey\n\n"
            "Instructions:\n"
            "1. In a microwave-safe mug, whisk together the egg and applesauce until smooth.\n"
            "2. Add protein powder, cocoa powder, almond flour, baking powder and salt. "
            "Stir until a smooth batter forms with no dry pockets.\n"
            "3. Fold in chocolate chips if using.\n"
            "4. Microwave on high for 60–90 seconds. The cake should be set on top but still "
            "slightly moist in the centre — it will firm up as it cools.\n"
            "5. Let it cool for 1 minute, then eat straight from the mug or flip onto a plate. "
            "Drizzle with honey if desired."
        ),
        "image_url": "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=600",
        "goal": "cheat",
        "calories": 260,
        "protein": 30.0,
        "carbs": 14.0,
        "fat": 9.0,
        "fiber": 3.0,
        "sugar": 5.0,
    },
    {
        "name": "Cauliflower Crust Margherita Pizza",
        "description": (
            "Serves 1 (personal pizza) | Prep: 15 min | Cook: 20 min\n\n"
            "Ingredients:\n"
            "• 250 g cauliflower florets (about ½ medium head)\n"
            "• 1 large egg\n"
            "• 40 g shredded mozzarella (for crust)\n"
            "• 1 tbsp almond flour\n"
            "• ½ tsp garlic powder, ½ tsp dried oregano, pinch of salt\n"
            "Topping:\n"
            "• 3 tbsp marinara sauce\n"
            "• 50 g fresh mozzarella, sliced\n"
            "• 5–6 fresh basil leaves\n"
            "• ½ tsp olive oil (for drizzle)\n\n"
            "Instructions:\n"
            "1. Preheat oven to 220 °C (425 °F). Line a baking sheet with parchment paper.\n"
            "2. Rice the cauliflower in a food processor until fine crumbles. "
            "Microwave for 4 minutes, then squeeze out ALL moisture using a clean kitchen towel — "
            "this is the most important step for a crispy crust.\n"
            "3. Mix dry cauliflower with egg, shredded mozzarella, almond flour, garlic powder, "
            "oregano and salt. Shape into a thin round (about 25 cm / 10 inches) on the parchment.\n"
            "4. Bake the crust alone for 12–14 minutes until golden and firm enough to lift.\n"
            "5. Spread marinara sauce, lay fresh mozzarella slices on top. "
            "Return to oven for 5–6 minutes until cheese melts and bubbles.\n"
            "6. Top with fresh basil, drizzle with olive oil, slice and serve."
        ),
        "image_url": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=600",
        "goal": "cheat",
        "calories": 340,
        "protein": 26.0,
        "carbs": 18.0,
        "fat": 16.0,
        "fiber": 5.0,
        "sugar": 8.0,
    },
    {
        "name": "Frozen Greek Yogurt Bark",
        "description": (
            "Serves 4 | Prep: 10 min | Freeze: 2 hours | No cooking required\n\n"
            "Ingredients:\n"
            "• 400 g Greek yogurt (0% or 2% fat)\n"
            "• 2 tbsp honey (30 g)\n"
            "• 1 tsp vanilla extract\n"
            "• 60 g mixed berries (blueberries, raspberries, sliced strawberries)\n"
            "• 20 g dark chocolate chips\n"
            "• 15 g unsweetened coconut flakes\n"
            "• 15 g crushed pistachios\n\n"
            "Instructions:\n"
            "1. Line a baking sheet with parchment paper.\n"
            "2. In a bowl, stir together Greek yogurt, honey and vanilla until smooth.\n"
            "3. Spread the yogurt mixture evenly onto the parchment in a thin layer "
            "(about 0.5 cm thick, roughly 25 × 35 cm rectangle).\n"
            "4. Scatter berries, chocolate chips, coconut flakes and pistachios over the surface. "
            "Press them gently into the yogurt.\n"
            "5. Freeze for at least 2 hours until completely solid.\n"
            "6. Break into irregular pieces (like bark). Store in a sealed container in the freezer "
            "for up to 2 weeks. Nutritional info is per serving (¼ of total)."
        ),
        "image_url": "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=600",
        "goal": "cheat",
        "calories": 180,
        "protein": 14.0,
        "carbs": 20.0,
        "fat": 5.0,
        "fiber": 2.0,
        "sugar": 16.0,
    },
    {
        "name": "Protein Ice Cream (3-Ingredient)",
        "description": (
            "Serves 1 | Prep: 5 min | Freeze: 1 min (blender) | No cooking required\n\n"
            "Ingredients:\n"
            "• 2 medium frozen bananas (about 200 g, sliced and frozen overnight)\n"
            "• 1 scoop (30 g) vanilla or chocolate whey protein\n"
            "• 2 tbsp unsweetened almond milk (30 ml)\n"
            "• Optional toppings: 10 g crushed nuts, 1 tsp honey, cinnamon\n\n"
            "Instructions:\n"
            "1. Add frozen banana slices, protein powder and almond milk to a food processor "
            "or high-speed blender.\n"
            "2. Blend for 30–45 seconds, scraping down the sides once. The mixture will first "
            "look crumbly, then suddenly turn into a thick, creamy soft-serve consistency.\n"
            "3. Do NOT over-blend — if it becomes too liquid, pop the bowl into the freezer "
            "for 15 minutes.\n"
            "4. Scoop into a bowl and add toppings if desired. Eat immediately for soft-serve "
            "texture, or freeze for 20–30 minutes for firmer ice cream."
        ),
        "image_url": "https://images.unsplash.com/photo-1570197571499-166b36435e9f?w=600",
        "goal": "cheat",
        "calories": 290,
        "protein": 28.0,
        "carbs": 42.0,
        "fat": 3.0,
        "fiber": 4.0,
        "sugar": 24.0,
    },
    {
        "name": "Turkey Lettuce Wrap Tacos",
        "description": (
            "Serves 1 (3 tacos) | Prep: 5 min | Cook: 10 min\n\n"
            "Ingredients:\n"
            "• 200 g lean ground turkey\n"
            "• ½ tsp cumin, ½ tsp chili powder, ½ tsp garlic powder\n"
            "• ¼ tsp smoked paprika, salt & pepper\n"
            "• 1 tsp olive oil\n"
            "• 3 large butter lettuce or iceberg leaves (as taco shells)\n"
            "• 30 g pico de gallo or fresh salsa\n"
            "• 20 g shredded cheese (cheddar or Mexican blend)\n"
            "• 1 tbsp Greek yogurt (instead of sour cream)\n"
            "• Squeeze of lime\n\n"
            "Instructions:\n"
            "1. Heat olive oil in a skillet over medium-high heat. Add ground turkey, break it up "
            "with a spatula, and cook for 5–6 minutes until no longer pink.\n"
            "2. Add cumin, chili powder, garlic powder, paprika, salt and pepper. Stir and cook "
            "for another 2 minutes until fragrant.\n"
            "3. Wash and dry the lettuce leaves — choose large, cupped ones that hold filling well.\n"
            "4. Divide the seasoned turkey among the three lettuce cups.\n"
            "5. Top each with pico de gallo, shredded cheese, a dollop of Greek yogurt and "
            "a squeeze of lime. Serve immediately."
        ),
        "image_url": "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=600",
        "goal": "cheat",
        "calories": 380,
        "protein": 42.0,
        "carbs": 8.0,
        "fat": 18.0,
        "fiber": 2.0,
        "sugar": 3.0,
    },

]

# Georgian translations keyed by English meal name.
# Applied automatically during seeding.
GEORGIAN_TRANSLATIONS: dict[str, dict[str, str]] = {
    "Grilled Chicken Breast with Steamed Broccoli": {
        "name_ka": "შემწვარი ქათმის ფილე ორთქლზე მოხარშულ ბროკოლისთან ერთად",
        "description_ka": (
            "ულუფა: 1 | წინასწარი მომზადება: 10 წთ | მომზადების დრო: 20 წთ\n\n"
            "ინგრედიენტები:\n"
            "• 200 გ ქათმის ფილე (1 საშუალო ნაჭერი)\n"
            "• 1 ჩ.კ. ზეითუნის ზეთი\n"
            "• 1 კბილი ნიორი, დაჭყლეტილი\n"
            "• ½ ჩ.კ. შებოლილი პაპრიკა\n"
            "• ½ ლიმონის წვენი\n"
            "• მარილი და შავი პილპილი გემოვნებით\n"
            "• 200 გ ბროკოლი (დაახლოებით 2 ჭიქა)\n"
            "• 1 ჩ.კ. დაბალმარილიანი სოიოს სოუსი\n"
            "• ½ ჩ.კ. სეზამის ზეთი\n\n"
            "მომზადების წესი:\n"
            "1. ქათმის ფილე სიბრტყეზე ისე გაჭერით, რომ თანაბარი სისქის იყოს (დაახლოებით 1.5 სმ). "
            "წაუსვით ზეითუნის ზეთი, დაჭყლეტილი ნიორი, პაპრიკა, ლიმონის წვენი, მარილი და პილპილი. "
            "გააჩერეთ მარინადში მინიმუმ 5 წუთი.\n"
            "2. გააცხელეთ გრილის ტაფა ან გარე გრილი საშუალოზე მაღალ ტემპერატურაზე (დაახლოებით 200 °C / 400 °F). "
            "შეწვით ქათამი 5–6 წუთის განმავლობაში თითოეულ მხარეს, სანამ შიდა ტემპერატურა არ მიაღწევს 74 °C-ს (165 °F). "
            "დაჭრამდე გააჩერეთ 3 წუთი.\n"
            "3. სანამ ქათამი იწვება, აადუღეთ წყალი ქვაბში. მოხარშეთ ბროკოლი ორთქლზე 4–5 წუთის განმავლობაში, "
            "სანამ არ გახდება ღია მწვანე და ოდნავ ხრაშუნა.\n"
            "4. ორთქლზე მოხარშულ ბროკოლის მოასხით სოიოს სოუსი და სეზამის ზეთი და კარგად აურიეთ.\n"
            "5. დაჭრილი ქათამი გადმოიღეთ თეფშზე ბროკოლისთან ერთად და მაშინვე მიირთვით."
        ),
    },
    "Tuna Poke Bowl": {
        "name_ka": "თინუსის პოკე ბოული",
        "description_ka": (
            "ულუფა: 1 | წინასწარი მომზადება: 15 წთ | მომზადების დრო: 5 წთ (ყვავილოვანი კომბოსტოს ბრინჯი)\n\n"
            "ინგრედიენტები:\n"
            "• 150 გ სუშის ხარისხის აჰი თინუსი, დაჭრილი 1.5 სმ კუბებად\n"
            "• 1 ს.კ. დაბალმარილიანი სოიოს სოუსი\n"
            "• 1 ჩ.კ. სეზამის ზეთი\n"
            "• ½ ჩ.კ. ბრინჯის ძმარი\n"
            "• 150 გ დაქუცმაცებული ყვავილოვანი კომბოსტო (ახალი ან გაყინული)\n"
            "• 50 გ კიტრი, კუბებად დაჭრილი\n"
            "• 40 გ გარჩეული ედამამე\n"
            "• 1 ს.კ. მარინირებული ჯანჯაფილი\n"
            "• 1 ჩ.კ. ფურიკაკეს სუნელი\n"
            "• სურვილისამებრ: ნორის თხელი ფირფიტები, სეზამის მარცვლები\n\n"
            "მომზადების წესი:\n"
            "1. ჯამში შეურიეთ თინუსის კუბები სოიოს სოუსს, სეზამის ზეთს და ბრინჯის ძმარს. "
            "მსუბუქად აურიეთ და შედგით მაცივარში 10 წუთით.\n"
            "2. გააცხელეთ მიწვის საწინააღმდეგო ტაფა საშუალო ცეცხლზე. დაამატეთ ყვავილოვანი კომბოსტოს ბრინჯი "
            "და თუშეთ 3–4 წუთის განმავლობაში, დროდადრო ურიეთ. შეაზავეთ მწიკვი მარილით.\n"
            "3. ყვავილოვანი კომბოსტოს ბრინჯი მოათავსეთ განიერ ჯამში. ზემოდან დაალაგეთ მარინირებული თინუსი, "
            "კიტრი, ედამამე და მარინირებული ჯანჯაფილი.\n"
            "4. მოაყარეთ ფურიკაკე და სეზამის მარცვლები. მიირთვით დაუყოვნებლივ — არ შეწვათ თინუსი."
        ),
    },
    "Egg White Veggie Omelette": {
        "name_ka": "კვერცხის ცილის ომლეტი ბოსტნეულით",
        "description_ka": (
            "ულუფა: 1 | წინასწარი მომზადება: 5 წთ | მომზადების დრო: 8 წთ\n\n"
            "ინგრედიენტები:\n"
            "• 6 დიდი კვერცხის ცილა (დაახლოებით 180 მლ)\n"
            "• 30 გ ახალი ისპანახი\n"
            "• 40 გ თეთრი სოკო, დაჭრილი\n"
            "• 30 გ წითელი ბულგარული წიწაკა, კუბებად დაჭრილი\n"
            "• 20 გ ყველი ფეტა, დაფხვნილი\n"
            "• 1 ჩ.კ. ზეითუნის ზეთი ან სპრეი-ზეთი\n"
            "• მარილი და პილპილი გემოვნებით\n"
            "• 6–8 ჩერი პომიდორი (გასაფორმებლად)\n\n"
            "მომზადების წესი:\n"
            "1. ათქვიფეთ კვერცხის ცილა მწიკვ მარილთან და პილპილთან ერთად ოდნავ აქაფებამდე.\n"
            "2. გააცხელეთ ზეითუნის ზეთი 24 სმ-იან ტაფაზე საშუალო ცეცხლზე. მოთუშეთ სოკო და ბულგარული წიწაკა "
            "2–3 წუთის განმავლობაში, სანამ არ დარბილდება. დაამატეთ ისპანახი და შუშეთ 30 წამი. "
            "გადაიტანეთ ბოსტნეული თეფშზე.\n"
            "3. გაწმინდეთ ტაფა, დაამატეთ ცოტაოდენი ზეთი და დაასხით კვერცხის ცილა. "
            "ტაფა გადახარეთ, რომ ცილა თანაბრად გადანაწილდეს. წვით ხელშეუხებლად 2 წუთი, სანამ კიდეები არ შეიკვრება.\n"
            "4. მოთუშული ბოსტნეული და ფეტა გაანაწილეთ ომლეტის ერთ ნახევარზე. "
            "გადააფარეთ მეორე ნახევარი და წვით კიდევ 1–2 წუთი.\n"
            "5. გადაიტანეთ თეფშზე, გვერდით დაუდეთ შუაზე გაჭრილი ჩერი პომიდვრები და მიირთვით."
        ),
    },
    "Greek Yogurt Protein Bowl": {
        "name_ka": "ბერძნული იოგურტის პროტეინის ჯამი",
        "description_ka": (
            "ულუფა: 1 | წინასწარი მომზადება: 5 წთ | არ საჭიროებს თერმულ დამუშავებას\n\n"
            "ინგრედიენტები:\n"
            "• 200 გ ბერძნული იოგურტი (0% ცხიმიანობით)\n"
            "• 60 გ კენკრის მიქსი (მოცვი, ჟოლო, მარწყვი)\n"
            "• 1 ს.კ. თაფლი (დაახლოებით 15 გ)\n"
            "• 1 ს.კ. ჩიას თესლი (10 გ)\n"
            "• 15 გ ნედლი ნუში (დაახლოებით 10 ცალი)\n"
            "• სურვილისამებრ: პიტნის რამდენიმე ახალი ფოთოლი\n\n"
            "მომზადების წესი:\n"
            "1. გადაიტანეთ ბერძნული იოგურტი ჯამში.\n"
            "2. გარეცხეთ კენკრა. მარწყვის გამოყენების შემთხვევაში, მოაჭერით ყუნწი და გაჭერით შუაზე.\n"
            "3. დაალაგეთ კენკრა იოგურტზე. მოასხით თაფლი.\n"
            "4. ზემოდან მოაყარეთ ჩიას თესლი და ნუში.\n"
            "5. საუკეთესო ტექსტურისთვის, გააჩერეთ 2–3 წუთი, რომ ჩიას თესლი გაფუვდეს, შემდეგ მიირთვით. "
            "ასევე შეგიძლიათ წინა ღამით ქილაში მოამზადოთ — მაცივარში ერთი ღამის განმავლობაში ჩიას თესლი "
            "პუდინგის მსგავს კონსისტენციას შექმნის."
        ),
    },
    "Shrimp Stir-Fry with Zucchini Noodles": {
        "name_ka": "კრევეტები ყაბაყის ნუდლსით",
        "description_ka": (
            "ულუფა: 1 | წინასწარი მომზადება: 10 წთ | მომზადების დრო: 8 წთ\n\n"
            "ინგრედიენტები:\n"
            "• 180 გ დიდი კრევეტი, გარჩეული და გასუფთავებული (დაახლოებით 10 ცალი)\n"
            "• 2 საშუალო ყაბაყი (დაახლოებით 300 გ), სპირალურად დაჭრილი ნუდლსის ფორმაზე\n"
            "• 2 კბილი ნიორი, დაჭყლეტილი\n"
            "• 1 ჩ.კ. ახალი ჯანჯაფილი, წვრილად გახეხილი\n"
            "• ¼ ჩ.კ. წითელი წიწაკის ფანტელები\n"
            "• 1 ჩ.კ. ზეითუნის ზეთი\n"
            "• ½ ლაიმის წვენი\n"
            "• 1 ჩ.კ. დაბალმარილიანი სოიოს სოუსი\n"
            "• მარილი გემოვნებით\n\n"
            "მომზადების წესი:\n"
            "1. შეამშრალეთ კრევეტები ქაღალდის ხელსახოცით და მსუბუქად მოაყარეთ მარილი.\n"
            "2. დიდ ტაფაზე (ან ვოკზე) მაღალ ცეცხლზე გააცხელეთ ზეითუნის ზეთი. დაალაგეთ კრევეტები ერთ ფენად "
            "და შეწვით 1.5 წუთის განმავლობაში თითოეულ მხარეს, სანამ არ გახდება ვარდისფერი და გაუმჭვირვალე. "
            "გადმოიღეთ თეფშზე.\n"
            "3. იგივე ტაფაზე დაამატეთ ნიორი, ჯანჯაფილი და წიწაკის ფანტელები. "
            "ურიეთ 30 წამის განმავლობაში, არომატის გამოყოფამდე.\n"
            "4. დაამატეთ ყაბაყის ნუდლსი. მოთუშეთ მაღალ ცეცხლზე 2–3 წუთის განმავლობაში — "
            "ის უნდა გათბეს, მაგრამ დარჩეს ოდნავ მკვრივი და არ ჩაიშალოს.\n"
            "5. დააბრუნეთ კრევეტები ტაფაში. დაამატეთ სოიოს სოუსი და ლაიმის წვენი, "
            "კარგად აურიეთ ყველაფერი 30 წამის განმავლობაში და დაუყოვნებლივ მიირთვით."
        ),
    },
    "Double Chicken Burrito Bowl": {
        "name_ka": "ბურიტოს ჯამი ორმაგი ქათმით",
        "description_ka": (
            "ულუფა: 1 | წინასწარი მომზადება: 15 წთ | მომზადების დრო: 25 წთ\n\n"
            "ინგრედიენტები:\n"
            "• 250 გ ქათმის ბარკლის რბილობი (ძვლის გარეშე), დაჭრილი 2 სმ-ის ნაჭრებად\n"
            "• 1 ჩ.კ. ძირა, ½ ჩ.კ. ჩილის ფხვნილი, ½ ჩ.კ. ნივრის ფხვნილი, მარილი და პილპილი\n"
            "• 1 ჩ.კ. ზეითუნის ზეთი\n"
            "• 120 გ თეთრი ბრინჯი (მშრალი წონა — მოხარშული გამოვა დაახლოებით 300 გ)\n"
            "• ½ ლაიმის წვენი + 1 ს.კ. დაჭრილი ქინძი (ბრინჯისთვის)\n"
            "• 80 გ დაკონსერვებული შავი ლობიო, გადაწურული და გარეცხილი\n"
            "• 50 გ შემწვარი სიმინდი (ტაფაზე მობრაწული)\n"
            "• 40 გ გუაკამოლე (დაახლოებით 2 ს.კ.)\n"
            "• 30 გ სალსა\n"
            "• 1 ს.კ. არაჟანი\n\n"
            "მომზადების წესი:\n"
            "1. მოხარშეთ ბრინჯი შეფუთვაზე მითითებული წესის მიხედვით (1:2 პროპორციით წყალთან, "
            "ხარშეთ თავდახურული 15 წთ). ააფხვიერეთ ჩანგლით და შეურიეთ ლაიმის წვენი და ქინძი.\n"
            "2. ქათმის ნაჭრებს შეაზილეთ ძირა, ჩილის ფხვნილი, ნივრის ფხვნილი, მარილი და პილპილი.\n"
            "3. გააცხელეთ ზეითუნის ზეთი დიდ ტაფაზე საშუალოზე მაღალ ცეცხლზე. შეწვით ქათამი 6–8 წუთის "
            "განმავლობაში, სანამ არ დაიბრაწება და კარგად არ შეიწვება (შიდა ტემპერატურა 74 °C / 165 °F).\n"
            "4. გაათბეთ შავი ლობიო პატარა ქვაბში ან მიკროტალღურ ღუმელში (1 წთ). "
            "სიმინდი ტაფაზე, ზეთის გარეშე, მობრაწეთ 2 წუთის განმავლობაში.\n"
            "5. აწყობა: ჯამში მოათავსეთ ქინძიანი და ლაიმიანი ბრინჯი, ზემოდან დაადეთ ქათამი, "
            "შავი ლობიო, სიმინდი, გუაკამოლე, სალსა და არაჟანი."
        ),
    },
    "Beef & Sweet Potato Power Plate": {
        "name_ka": "ძროხის ხორცისა და ტკბილი კარტოფილის ენერგეტიკული თეფში",
        "description_ka": (
            "ულუფა: 1 | წინასწარი მომზადება: 10 წთ | მომზადების დრო: 30 წთ\n\n"
            "ინგრედიენტები:\n"
            "• 200 გ მჭლე ძროხის ფარში (90/10)\n"
            "• 1 საშუალო ტკბილი კარტოფილი (ბატატი, დაახლოებით 200 გ), გათლილი და 2 სმ-ის კუბებად დაჭრილი\n"
            "• 150 გ მწვანე ლობიო (პარკი), ბოლოებმოჭრილი\n"
            "• ½ საშუალო ხახვი, კუბებად დაჭრილი\n"
            "• 2 კბილი ნიორი, დაჭყლეტილი\n"
            "• 1 ჩ.კ. ზეითუნის ზეთი\n"
            "• მარილი, პილპილი, ½ ჩ.კ. შებოლილი პაპრიკა\n\n"
            "მომზადების წესი:\n"
            "1. გააცხელეთ ღუმელი 200 °C-მდე (400 °F). ტკბილი კარტოფილის კუბებს შეურიეთ ½ ჩ.კ. ზეითუნის ზეთი, "
            "მარილი და პაპრიკა. გაანაწილეთ საცხობ ქაღალდდაფენილ ლანგარზე ერთ ფენად. გამოაცხვეთ 22–25 წუთის "
            "განმავლობაში, შუა პროცესში გადააბრუნეთ, სანამ არ გახდება ოქროსფერი.\n"
            "2. სანამ ტკბილი კარტოფილი ცხვება, დიდ ტაფაზე გააცხელეთ ½ ჩ.კ. ზეითუნის ზეთი. "
            "მოთუშეთ ხახვი 3 წუთის განმავლობაში, შემდეგ დაამატეთ ნიორი და თუშეთ კიდევ 30 წამი.\n"
            "3. დაამატეთ ძროხის ფარში, დააქუცმაცეთ ნიჩბით და წვით 6–7 წუთის განმავლობაში, "
            "სანამ არ შეყავისფრდება. შეაზავეთ მარილით და პილპილით. გადაღვარეთ ზედმეტი ცხიმი.\n"
            "4. მოხარშეთ მწვანე ლობიო ორთქლზე ან წყალში 4–5 წუთის განმავლობაში.\n"
            "5. თეფშზე ერთმანეთის გვერდით მოათავსეთ ძროხის ხორცი, ტკბილი კარტოფილი და მწვანე ლობიო. "
            "მიირთვით ცხელი."
        ),
    },
    "Salmon & Quinoa Bowl": {
        "name_ka": "ორაგულისა და კინოას ჯამი",
        "description_ka": (
            "ულუფა: 1 | წინასწარი მომზადება: 10 წთ | მომზადების დრო: 25 წთ\n\n"
            "ინგრედიენტები:\n"
            "• 180 გ ატლანტიკური ორაგულის ფილე (კანით ან კანის გარეშე)\n"
            "• 1 ს.კ. დიჟონის მდოგვი + 1 ჩ.კ. თაფლი (ჭიქურისთვის)\n"
            "• 80 გ კინოა (მშრალი წონა — მოხარშული გამოვა დაახლოებით 200 გ)\n"
            "• 100 გ სატაცური (დაახლოებით 6 ღერო), ბოლოებმოჭრილი\n"
            "• 1 ჩ.კ. ზეითუნის ზეთი\n"
            "• ½ ლიმონის წვენი\n"
            "• მარილი და პილპილი გემოვნებით\n\n"
            "მომზადების წესი:\n"
            "1. გააცხელეთ ღუმელი 200 °C-მდე (400 °F). პატარა საცხობ ლანგარზე დააფინეთ პერგამენტის ქაღალდი.\n"
            "2. გარეცხეთ კინოა წვრილ საცერში. მოათავსეთ ქვაბში 160 მლ წყალთან და მწიკვ მარილთან ერთად. "
            "აადუღეთ, დაუწიეთ ცეცხლს, დაახურეთ თავზე და ხარშეთ 15 წუთი. გადმოდგით, გააჩერეთ 5 წუთი, "
            "შემდეგ ააფხვიერეთ ჩანგლით.\n"
            "3. მოათავსეთ ორაგული საცხობ ლანგარზე. ერთმანეთს შეურიეთ მდოგვი და თაფლი, "
            "წაუსვით ორაგულს ზემოდან. შეაზავეთ მარილით და პილპილით.\n"
            "4. სატაცურს მოასხით ზეითუნის ზეთი და მარილი, შემოუწყვეთ ორაგულს გარშემო.\n"
            "5. გამოაცხვეთ 12–15 წუთის განმავლობაში, სანამ ორაგული ადვილად არ დაიშლება "
            "(შიდა ტემპერატურა 52 °C / 125 °F).\n"
            "6. თეფშზე მოათავსეთ კინოა, ზემოდან დაადეთ ორაგული, გვერდით სატაცური, "
            "და ბოლოს მოასხით ახალი ლიმონის წვენი."
        ),
    },
    "Peanut Butter Banana Protein Shake": {
        "name_ka": "არაქისის კარაქისა და ბანანის პროტეინის შეიკი",
        "description_ka": (
            "ულუფა: 1 | წინასწარი მომზადება: 5 წთ | არ საჭიროებს თერმულ დამუშავებას\n\n"
            "ინგრედიენტები:\n"
            "• 300 მლ სრულცხიმიანი რძე\n"
            "• 2 კოვზი (60 გ) შრატის ცილა (ვანილის ან შოკოლადის)\n"
            "• 1 მწიფე ბანანი (დაახლოებით 120 გ)\n"
            "• 2 ს.კ. ნატურალური არაქისის კარაქი (32 გ)\n"
            "• 30 გ შვრიის ფანტელები\n"
            "• 3–4 ყინულის კუბიკი\n"
            "• სურვილისამებრ: 1 ჩ.კ. თაფლი, მწიკვი დარიჩინი\n\n"
            "მომზადების წესი:\n"
            "1. ბლენდერში ჩაყარეთ შვრია და დააბლენდერეთ რამდენჯერმე, სანამ უხეში ფქვილის ფორმას "
            "არ მიიღებს — ეს შეიკს უფრო ერთგვაროვანს გახდის.\n"
            "2. დაამატეთ რძე, პროტეინის ფხვნილი, ბანანი (ნაჭრებად), "
            "არაქისის კარაქი და ყინულის კუბიკები.\n"
            "3. დააბლენდერეთ მაღალ სიჩქარეზე 45–60 წამის განმავლობაში, "
            "სანამ სრულად ერთგვაროვანი და აქაფებული არ გახდება.\n"
            "4. ჩამოასხით დიდ ჭიქაში. შეიკი საკმაოდ სქელია — "
            "თუ უფრო თხელი კონსისტენცია გირჩევნიათ, დაამატეთ 50 მლ რძე.\n"
            "5. საუკეთესო გემოსა და ტექსტურისთვის დალიეთ მომზადებიდან 30 წუთის განმავლობაში. "
            "იდეალურია ვარჯიშის შემდეგ ან დილის წახემსებისას."
        ),
    },
    "Pasta with Turkey Meatballs": {
        "name_ka": "პასტა ინდაურის ხორცის გუფთებით",
        "description_ka": (
            "ულუფა: 1 | წინასწარი მომზადება: 15 წთ | მომზადების დრო: 25 წთ\n\n"
            "ინგრედიენტები:\n"
            "• 100 გ მთელმარცვლოვანი პენე (მშრალი წონა)\n"
            "• 200 გ მჭლე ინდაურის ფარში\n"
            "• 1 კბილი ნიორი, დაჭყლეტილი\n"
            "• 1 ს.კ. საფანელი\n"
            "• 1 ჩ.კ. ხმელი ორეგანო, ½ ჩ.კ. ხმელი რეჰანი (ბაზილიკი)\n"
            "• 1 კვერცხის ცილა\n"
            "• მარილი და პილპილი\n"
            "• 150 მლ მარინარას სოუსი (მზა ან სახლში დამზადებული)\n"
            "• 15 გ გახეხილი პარმეზანი\n\n"
            "მომზადების წესი:\n"
            "1. ჯამში შეურიეთ ინდაურის ფარში, ნიორი, საფანელი, ორეგანო, რეჰანი, კვერცხის ცილა, "
            "მარილი და პილპილი. ხელით აურიეთ ინგრედიენტების შერწყმამდე — ზედმეტად ნუ ზილავთ. "
            "დაამრგვალეთ 5–6 გუფთად (თითოეული დაახლოებით 35 გ).\n"
            "2. გააცხელეთ მიწვის საწინააღმდეგო ტაფა საშუალო ცეცხლზე და მსუბუქად მოასხით ზეთი. "
            "შეწვით გუფთები 2–3 წუთის განმავლობაში თითოეულ მხარეს, სანამ ყველა მხრიდან არ შეიბრაწება.\n"
            "3. ჩაასხით ტაფაში მარინარას სოუსი, დაუწიეთ ცეცხლს, დაახურეთ თავზე და ხარშეთ 12–15 წუთი, "
            "სანამ გუფთები ბოლომდე არ მომზადდება (შიდა ტემპერატურა 74 °C / 165 °F).\n"
            "4. ამასობაში, მარილიან მდუღარე წყალში მოხარშეთ პენე (10–12 წთ). "
            "გადაწურეთ, შეინახეთ 2 ს.კ. პასტის ნახარში წყალი.\n"
            "5. აურიეთ პასტა გუფთებსა და სოუსში, საჭიროების შემთხვევაში დაამატეთ პასტის წყალი. "
            "მოაყარეთ გახეხილი პარმეზანი და მიირთვით."
        ),
    },
    "Mediterranean Chicken Wrap": {
        "name_ka": "ხმელთაშუაზღვიური ქათმის ვრაპი",
        "description_ka": (
            "ულუფა: 1 | წინასწარი მომზადება: 10 წთ | მომზადების დრო: 10 წთ\n\n"
            "ინგრედიენტები:\n"
            "• 150 გ ქათმის ფილე, თხელ ზოლებად დაჭრილი\n"
            "• 1 დიდი მთელმარცვლოვანი ტორტილა (დაახლოებით 60 გ)\n"
            "• 2 ს.კ. ჰუმუსი (30 გ)\n"
            "• 30 გ მწვანე ფოთლების მიქსი (რუკოლა, ისპანახი)\n"
            "• 4–5 მზეზე გამომშრალი პომიდორი, დაჭრილი\n"
            "• 2 თხელი ნაჭერი წითელი ხახვი\n"
            "• 20 გ ყველი ფეტა, დაფხვნილი\n"
            "• ½ ჩ.კ. ზეითუნის ზეთი\n"
            "• ½ ჩ.კ. ხმელი ორეგანო, მარილი და პილპილი\n\n"
            "მომზადების წესი:\n"
            "1. ქათმის ზოლები შეაზავეთ ორეგანოთი, მარილით და პილპილით. გააცხელეთ ზეითუნის ზეთი ტაფაზე "
            "საშუალოზე მაღალ ცეცხლზე და წვით ქათამი 4–5 წუთის განმავლობაში თითოეულ მხარეს.\n"
            "2. ტორტილა გაათბეთ მშრალ ტაფაზე 20 წამის განმავლობაში თითოეულ მხარეს "
            "ან მიკროტალღურ ღუმელში 10 წამით.\n"
            "3. ტორტილას შუაში წაუსვით ჰუმუსი. ფენებად დაალაგეთ მწვანე ფოთლები, შემწვარი ქათამი, "
            "მზეზე გამომშრალი პომიდორი, წითელი ხახვი და ფეტა.\n"
            "4. ქვედა კიდე გადმოკეცეთ ზემოთ, შემდეგ გვერდები მჭიდროდ გადაახვიეთ. "
            "გაჭერით შუაზე დიაგონალურად და მიირთვით. საკვების მარაგად კარგად ეხვევა ფოლგაში."
        ),
    },
    "Teriyaki Salmon Rice Bowl": {
        "name_ka": "ტერიაკი ორაგულის და ბრინჯის ჯამი",
        "description_ka": (
            "ულუფა: 1 | წინასწარი მომზადება: 10 წთ | მომზადების დრო: 20 წთ\n\n"
            "ინგრედიენტები:\n"
            "• 150 გ ორაგულის ფილე\n"
            "• 2 ს.კ. ტერიაკის სოუსი (მზა ან: 1 ს.კ. სოიოს სოუსი + 1 ჩ.კ. თაფლი + "
            "½ ჩ.კ. ბრინჯის ძმარი + ½ ჩ.კ. სიმინდის სახამებელი)\n"
            "• 100 გ ჟასმინის ბრინჯი (მშრალი — მოხარშული გამოვა დაახლოებით 250 გ)\n"
            "• 100 გ ბეიბი ბოკ-ჩოი, სიგრძეზე შუაზე გაჭრილი\n"
            "• 50 გ სტაფილო, ჟულიენად დაჭრილი\n"
            "• 1 ჩ.კ. სეზამის მარცვლები\n"
            "• 1 ჩ.კ. მცენარეული ზეთი\n\n"
            "მომზადების წესი:\n"
            "1. მოხარშეთ ჟასმინის ბრინჯი: გარეცხეთ, შეურიეთ 150 მლ წყალს, აადუღეთ, "
            "დაუწიეთ ცეცხლს, დაახურეთ და ხარშეთ 12 წუთი. გააჩერეთ თავდახურული 5 წუთი.\n"
            "2. შეამშრალეთ ორაგული. წაუსვით ტერიაკის სოუსის ნახევარი.\n"
            "3. გააცხელეთ ზეთი ტაფაზე საშუალოზე მაღალ ცეცხლზე. მოათავსეთ ორაგული კანიანი მხრიდან "
            "ზემოთ და წვით 3 წუთი. გადააბრუნეთ და წვით კიდევ 3–4 წუთი. "
            "ბოლო წუთის განმავლობაში წაუსვით დარჩენილი ტერიაკის სოუსი.\n"
            "4. იმავე ტაფაზე მოთუშეთ ბოკ-ჩოი და სტაფილო 2 წუთის განმავლობაში მაღალ ცეცხლზე.\n"
            "5. აწყობა: ბრინჯი მოათავსეთ ჯამში, ზემოდან ორაგული, გვერდით ბოსტნეული. "
            "მოაყარეთ სეზამის მარცვლები."
        ),
    },
    "Turkey & Avocado Sandwich": {
        "name_ka": "ინდაურისა და ავოკადოს სენდვიჩი",
        "description_ka": (
            "ულუფა: 1 | წინასწარი მომზადება: 5 წთ | არ საჭიროებს თერმულ დამუშავებას\n\n"
            "ინგრედიენტები:\n"
            "• 2 ნაჭერი საფუვრიანი პური (sourdough, ჯამში დაახლოებით 70 გ)\n"
            "• 120 გ დაჭრილი შემწვარი ინდაურის მკერდი\n"
            "• ½ მწიფე ავოკადო (დაახლოებით 60 გ), დაჭრილი\n"
            "• 2 ნაჭერი მწიფე პომიდორი\n"
            "• 2–3 ფოთოლი სალათის ფურცელი\n"
            "• 1 ჩ.კ. დიჟონის მდოგვი\n"
            "• მარილი და პილპილი გემოვნებით\n\n"
            "მომზადების წესი:\n"
            "1. გახუხეთ პურის ნაჭრები ოქროსფრამდე (ტოსტერში ან მშრალ ტაფაზე, 2 წუთი თითოეულ მხარეს).\n"
            "2. ერთ ნაჭერს წაუსვით დიჟონის მდოგვი.\n"
            "3. ფენებად დაალაგეთ ინდაური, ავოკადოს ნაჭრები, პომიდორი და სალათის ფურცელი. "
            "შეაზავეთ მწიკვი მარილითა და პილპილით.\n"
            "4. დააფარეთ მეორე ნაჭერი, ოდნავ დააწექით და დიაგონალურად გაჭერით შუაზე.\n"
            "5. საუკეთესოა ახლად მომზადებული. მარაგად შენახვისას, ავოკადო შეინახეთ ცალკე "
            "და დაამატეთ ჭამის წინ, რათა არ გამუქდეს."
        ),
    },
    "Grilled Steak Salad": {
        "name_ka": "შემწვარი სტეიკის სალათი",
        "description_ka": (
            "ულუფა: 1 | წინასწარი მომზადება: 10 წთ | მომზადების დრო: 12 წთ\n\n"
            "ინგრედიენტები:\n"
            "• 180 გ სირლოინ სტეიკი (დაახლოებით 2 სმ სისქის)\n"
            "• 80 გ სალათის ფოთლების მიქსი\n"
            "• 8 ჩერი პომიდორი, შუაზე გაჭრილი\n"
            "• 2 თხელი ნაჭერი წითელი ხახვი\n"
            "• 25 გ ლურჯი ყველი (blue cheese), დაფხვნილი\n"
            "• 1 ს.კ. ბალზამიკოს ძმარი + 1 ჩ.კ. ზეითუნის ზეთი + ½ ჩ.კ. დიჟონის მდოგვი (დრესინგისთვის)\n"
            "• მარილი და პილპილი\n\n"
            "მომზადების წესი:\n"
            "1. გამოიღეთ სტეიკი მაცივრიდან შეწვამდე 20 წუთით ადრე. "
            "შეამშრალეთ და უხვად შეაზავეთ მარილით და პილპილით ორივე მხრიდან.\n"
            "2. გააცხელეთ თუჯის ტაფა ან გრილის ტაფა მაღალ ცეცხლზე, სანამ ბოლის გამოშვებას არ დაიწყებს. "
            "შეწვით სტეიკი 3–4 წუთი თითოეულ მხარეს საშუალო-ნაკლები შემწვარობისთვის "
            "(შიდა ტემპერატურა 55 °C / 130 °F). საშუალოსთვის — 4–5 წუთი (60 °C / 140 °F).\n"
            "3. დაასვენეთ სტეიკი საჭრელ დაფაზე 5 წუთის განმავლობაში, შემდეგ დაჭერით "
            "ბოჭკოების საწინააღმდეგო მიმართულებით 1 სმ-ის ზოლებად.\n"
            "4. სანამ სტეიკი ისვენებს, ათქვიფეთ ბალზამიკოს ძმარი, ზეითუნის ზეთი და დიჟონის მდოგვი.\n"
            "5. სალათის ფოთლები მოათავსეთ თეფშზე, ზემოდან დაალაგეთ პომიდორი, წითელი ხახვი "
            "და სტეიკის ნაჭრები. მოაყარეთ ლურჯი ყველი და მოასხით დრესინგი."
        ),
    },
    "High-Protein Chocolate Mug Cake": {
        "name_ka": "მაღალპროტეინიანი შოკოლადის კექსი ჭიქაში",
        "description_ka": (
            "ულუფა: 1 | წინასწარი მომზადება: 3 წთ | მომზადების დრო: 2 წთ (მიკროტალღური)\n\n"
            "ინგრედიენტები:\n"
            "• 1 კოვზი (30 გ) შოკოლადის შრატის ცილა\n"
            "• 1 ს.კ. კაკაოს ფხვნილი (უშაქრო)\n"
            "• 1 დიდი კვერცხი\n"
            "• 2 ს.კ. უშაქრო ვაშლის პიურე (30 გ)\n"
            "• 1 ს.კ. ნუშის ფქვილი (7 გ)\n"
            "• ½ ჩ.კ. საცხობი ფხვნილი\n"
            "• მწიკვი მარილი\n"
            "• სურვილისამებრ: 10 გ შავი შოკოლადის ჩიფსი, 1 ჩ.კ. თაფლი\n\n"
            "მომზადების წესი:\n"
            "1. მიკროტალღურ ღუმელში გამოსაყენებელ ჭიქაში ათქვიფეთ კვერცხი და ვაშლის პიურე.\n"
            "2. დაამატეთ პროტეინის ფხვნილი, კაკაო, ნუშის ფქვილი, საცხობი ფხვნილი და მარილი. "
            "აურიეთ გლუვ ცომამდე.\n"
            "3. სურვილისამებრ ჩააყარეთ შოკოლადის ჩიფსი.\n"
            "4. მიკროტალღურ ღუმელში გააცხელეთ მაქსიმუმზე 60–90 წამი. "
            "კექსი ზემოდან მყარი უნდა იყოს, შუაში — ოდნავ ნოტიო.\n"
            "5. გააჩერეთ 1 წუთი, შემდეგ მიირთვით ჭიქიდანვე ან ამოაბრუნეთ თეფშზე."
        ),
    },
    "Cauliflower Crust Margherita Pizza": {
        "name_ka": "ყვავილოვანი კომბოსტოს პიცა მარგარიტა",
        "description_ka": (
            "ულუფა: 1 (პერსონალური პიცა) | წინასწარი მომზადება: 15 წთ | მომზადების დრო: 20 წთ\n\n"
            "ინგრედიენტები:\n"
            "• 250 გ ყვავილოვანი კომბოსტო\n"
            "• 1 დიდი კვერცხი\n"
            "• 40 გ გახეხილი მოცარელა (ცომისთვის)\n"
            "• 1 ს.კ. ნუშის ფქვილი\n"
            "• ½ ჩ.კ. ნივრის ფხვნილი, ½ ჩ.კ. ხმელი ორეგანო, მწიკვი მარილი\n"
            "შიგთავსი:\n"
            "• 3 ს.კ. მარინარას სოუსი\n"
            "• 50 გ ახალი მოცარელა, დაჭრილი\n"
            "• 5–6 ახალი რეჰნის ფოთოლი\n"
            "• ½ ჩ.კ. ზეითუნის ზეთი\n\n"
            "მომზადების წესი:\n"
            "1. გააცხელეთ ღუმელი 220 °C-მდე (425 °F).\n"
            "2. დაქუცმაცეთ ყვავილოვანი კომბოსტო ბრინჯის ფორმამდე. "
            "მიკროტალღურ ღუმელში გააჩერეთ 4 წუთი, შემდეგ გამოწურეთ მთელი ტენიანობა ხელსახოცით.\n"
            "3. შეურიეთ კვერცხი, მოცარელა, ნუშის ფქვილი და სუნელები. "
            "გააბრტყელეთ თხელ წრედ (დაახლოებით 25 სმ) პერგამენტის ქაღალდზე.\n"
            "4. გამოაცხვეთ ცომი 12–14 წუთი, სანამ არ გახდება ოქროსფერი.\n"
            "5. წაუსვით სოუსი, დაალაგეთ მოცარელა. გამოაცხვეთ კიდევ 5–6 წუთი.\n"
            "6. მოაყარეთ ახალი რეჰანი, მოასხით ზეითუნის ზეთი და მიირთვით."
        ),
    },
    "Frozen Greek Yogurt Bark": {
        "name_ka": "გაყინული ბერძნული იოგურტის ფირფიტა",
        "description_ka": (
            "ულუფა: 4 | წინასწარი მომზადება: 10 წთ | გაყინვა: 2 საათი\n\n"
            "ინგრედიენტები:\n"
            "• 400 გ ბერძნული იოგურტი (0% ან 2%)\n"
            "• 2 ს.კ. თაფლი (30 გ)\n"
            "• 1 ჩ.კ. ვანილის ექსტრაქტი\n"
            "• 60 გ კენკრის მიქსი\n"
            "• 20 გ შავი შოკოლადის ჩიფსი\n"
            "• 15 გ ქოქოსის ფანტელები\n"
            "• 15 გ დაფშვნილი ფისტა\n\n"
            "მომზადების წესი:\n"
            "1. საცხობ ლანგარზე დააფინეთ პერგამენტის ქაღალდი.\n"
            "2. ჯამში შეურიეთ იოგურტი, თაფლი და ვანილი.\n"
            "3. გადაიტანეთ ქაღალდზე თხელი ფენით (დაახლოებით 0.5 სმ).\n"
            "4. ზემოდან დაალაგეთ კენკრა, შოკოლადი, ქოქოსი და ფისტა. "
            "მსუბუქად დააჭირეთ იოგურტში.\n"
            "5. გაყინეთ მინიმუმ 2 საათი.\n"
            "6. დაამტვრიეთ ნაჭრებად. შეინახეთ საყინულეში 2 კვირამდე. "
            "საკვებ ნივთიერებათა მონაცემები 1 ულუფაზეა."
        ),
    },
    "Protein Ice Cream (3-Ingredient)": {
        "name_ka": "პროტეინის ნაყინი (3 ინგრედიენტი)",
        "description_ka": (
            "ულუფა: 1 | წინასწარი მომზადება: 5 წთ | არ საჭიროებს თერმულ დამუშავებას\n\n"
            "ინგრედიენტები:\n"
            "• 2 საშუალო გაყინული ბანანი (დაახლოებით 200 გ, დაჭრილი და გაყინული ერთი ღამით)\n"
            "• 1 კოვზი (30 გ) ვანილის ან შოკოლადის შრატის ცილა\n"
            "• 2 ს.კ. უშაქრო ნუშის რძე (30 მლ)\n"
            "• სურვილისამებრ: 10 გ დაფშვნილი თხილი, 1 ჩ.კ. თაფლი, დარიჩინი\n\n"
            "მომზადების წესი:\n"
            "1. ბლენდერში ან საკვების პროცესორში ჩაყარეთ გაყინული ბანანი, "
            "პროტეინის ფხვნილი და ნუშის რძე.\n"
            "2. დააბლენდერეთ 30–45 წამი, ერთხელ ჩამოფხეკეთ გვერდები. "
            "მასა ჯერ ფხვნილივით გამოჩნდება, შემდეგ კრემისებრი გახდება.\n"
            "3. ზედმეტად არ დააბლენდეროთ — თუ თხევადი გახდა, "
            "საყინულეში 15 წუთით დადგით.\n"
            "4. გადაიტანეთ ჯამში, მოაყარეთ შიგთავსი და მაშინვე მიირთვით."
        ),
    },
    "Turkey Lettuce Wrap Tacos": {
        "name_ka": "ინდაურის სალათის ტაკოსები",
        "description_ka": (
            "ულუფა: 1 (3 ტაკო) | წინასწარი მომზადება: 5 წთ | მომზადების დრო: 10 წთ\n\n"
            "ინგრედიენტები:\n"
            "• 200 გ მჭლე ინდაურის ფარში\n"
            "• ½ ჩ.კ. ძირა, ½ ჩ.კ. ჩილის ფხვნილი, ½ ჩ.კ. ნივრის ფხვნილი\n"
            "• ¼ ჩ.კ. შებოლილი პაპრიკა, მარილი და პილპილი\n"
            "• 1 ჩ.კ. ზეითუნის ზეთი\n"
            "• 3 დიდი სალათის ფოთოლი (ტაკოს გარსის ნაცვლად)\n"
            "• 30 გ სალსა\n"
            "• 20 გ გახეხილი ყველი\n"
            "• 1 ს.კ. ბერძნული იოგურტი (არაჟნის ნაცვლად)\n"
            "• ლაიმის წვენი\n\n"
            "მომზადების წესი:\n"
            "1. ტაფაზე გააცხელეთ ზეითუნის ზეთი. დაამატეთ ინდაურის ფარში "
            "და წვით 5–6 წუთი, დროდადრო ურიეთ.\n"
            "2. დაამატეთ ძირა, ჩილი, ნივრის ფხვნილი, პაპრიკა, მარილი და პილპილი. "
            "წვით კიდევ 2 წუთი.\n"
            "3. გარეცხეთ და შეამშრალეთ სალათის ფოთლები.\n"
            "4. გადაანაწილეთ შემწვარი ინდაური სამ ფოთოლში.\n"
            "5. ზემოდან დაადეთ სალსა, ყველი, იოგურტი და მოწურეთ ლაიმი. "
            "მაშინვე მიირთვით."
        ),
    },
}
