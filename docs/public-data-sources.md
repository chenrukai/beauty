# Public Data Sources

This project now includes a curated upgrade seed for public-facing beauty data.
The product and ingredient mappings below were compiled from official product pages
and used to expand the local SQL seed.

## Product References

- CeraVe Hydrating Facial Cleanser
  - https://www.cerave.com/skincare/cleansers/hydrating-facial-cleanser
- CeraVe PM Facial Moisturizing Lotion
  - https://www.cerave.com/en-us/skincare/moisturizers/pm-facial-moisturizing-lotion
- La Roche-Posay Effaclar Salicylic Acid Acne Treatment Serum
  - https://www.laroche-posay.us/our-products/face/acne-products/effaclar-salicylic-acid-acne-treatment-serum-3337875722827.html
- The Ordinary Niacinamide 10% + Zinc 1%
  - https://theordinary.com/en-us/niacinamide-10-zinc-1-serum-100436.html
- The Ordinary Hyaluronic Acid 2% + B5 (Original Formulation)
  - https://theordinary.com/en-us/hyaluronic-acid-2-b5-serum-original-formulation-100425.html

## Seed Strategy

- Keep the existing broad demo dataset for development screens.
- Add a smaller layer of named, real-world public products for user-facing demos.
- Map those products to existing ingredient/effect tables so chat and admin demos feel less synthetic.
