/**
 * NuGen Meal Planner - Color Palette
 * A soft, health-focused color palette (greens, soft whites, dark greys for text).
 */

const tintColorLight = '#4A7C59'; // Soft forest green
const tintColorDark = '#84A98C';

export const Colors = {
  light: {
    text: '#22223B', // Dark grey for readability
    background: '#F8F9FA', // Soft off-white
    tint: tintColorLight,
    icon: '#68748A',
    tabIconDefault: '#68748A',
    tabIconSelected: tintColorLight,
    surface: '#FFFFFF', // Pure white for cards
    border: '#E2E8F0',
    primary: '#4A7C59', // Green for primary actions
    secondary: '#84A98C', // Lighter green
    accent: '#F2CC8F', // Soft yellow for accents/highlights
    error: '#E07A5F', // Soft red
    success: '#81B29A', // Soft green
  },
  dark: {
    text: '#F8F9FA',
    background: '#22223B',
    tint: tintColorDark,
    icon: '#9BA4B5',
    tabIconDefault: '#9BA4B5',
    tabIconSelected: tintColorDark,
    surface: '#4A4E69',
    border: '#9BA4B5',
    primary: '#84A98C',
    secondary: '#4A7C59',
    accent: '#F2CC8F',
    error: '#E07A5F',
    success: '#81B29A',
  },
};
