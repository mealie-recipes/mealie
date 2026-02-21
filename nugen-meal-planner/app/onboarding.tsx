import { useState } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, Switch, SafeAreaView } from 'react-native';
import { useRouter } from 'expo-router';
import { useFoodStore } from '@/store/useFoodStore';
import { Colors } from '@/constants/Colors';
import { useColorScheme } from '@/hooks/useColorScheme';
import { Ingredient, IngredientCategory, UserPreferences } from '@/store/types';

// Mock initial ingredients
const INITIAL_INGREDIENTS: Omit<Ingredient, 'isSelected'>[] = [
    { id: '1', name: 'Chicken Breast', category: 'Proteins' },
    { id: '2', name: 'Tofu', category: 'Proteins' },
    { id: '3', name: 'Salmon', category: 'Proteins' },
    { id: '4', name: 'Broccoli', category: 'Veggies' },
    { id: '5', name: 'Spinach', category: 'Veggies' },
    { id: '6', name: 'Bell Peppers', category: 'Veggies' },
    { id: '7', name: 'Sweet Potato', category: 'Carbs' },
    { id: '8', name: 'Quinoa', category: 'Carbs' },
    { id: '9', name: 'Brown Rice', category: 'Carbs' },
    { id: '10', name: 'Olive Oil', category: 'Fats' },
    { id: '11', name: 'Avocado', category: 'Fats' },
    { id: '12', name: 'Kimchi', category: 'Fermented' },
    { id: '13', name: 'Garlic Powder', category: 'Spices' },
    { id: '14', name: 'Smoked Paprika', category: 'Spices' },
];

const CATEGORIES: IngredientCategory[] = ['Proteins', 'Veggies', 'Carbs', 'Fats', 'Fermented', 'Spices'];

export default function OnboardingScreen() {
    const router = useRouter();
    const colorScheme = useColorScheme();
    const colors = Colors[colorScheme ?? 'light'];

    const { setUserIngredients, setUserPreferences, completeSetup } = useFoodStore();

    const [step, setStep] = useState<1 | 2>(1);
    const [selectedIngredientIds, setSelectedIngredientIds] = useState<Set<string>>(new Set());

    // Step 2 Form State
    const [cookTime, setCookTime] = useState<number>(30);
    const [batchCook, setBatchCook] = useState<boolean>(false);

    const toggleIngredient = (id: string) => {
        const newSet = new Set(selectedIngredientIds);
        if (newSet.has(id)) {
            newSet.delete(id);
        } else {
            newSet.add(id);
        }
        setSelectedIngredientIds(newSet);
    };

    const handleNextStep = () => {
        if (selectedIngredientIds.size === 0) {
            alert('Please select at least one ingredient.');
            return;
        }
        setStep(2);
    };

    const handleFinishOnboarding = () => {
        // Save ingredients
        const finalIngredients: Ingredient[] = INITIAL_INGREDIENTS.map((ing) => ({
            ...ing,
            isSelected: selectedIngredientIds.has(ing.id),
        }));
        setUserIngredients(finalIngredients);

        // Save preferences
        setUserPreferences({
            cookTimeMinutes: cookTime,
            batchCookMode: batchCook,
        });

        // Complete setup and redirect
        completeSetup();
        router.replace('/(tabs)');
    };

    if (step === 1) {
        return (
            <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
                <ScrollView contentContainerStyle={styles.scrollContent}>
                    <Text style={[styles.header, { color: colors.text }]}>What's in your pantry?</Text>
                    <Text style={[styles.subHeader, { color: colors.icon }]}>Select the ingredients you like and have available.</Text>

                    {CATEGORIES.map((category) => {
                        const categoryIngredients = INITIAL_INGREDIENTS.filter((ing) => ing.category === category);
                        if (categoryIngredients.length === 0) return null;

                        return (
                            <View key={category} style={styles.categoryContainer}>
                                <Text style={[styles.categoryTitle, { color: colors.text }]}>{category}</Text>
                                <View style={styles.chipContainer}>
                                    {categoryIngredients.map((ing) => {
                                        const isSelected = selectedIngredientIds.has(ing.id);
                                        return (
                                            <TouchableOpacity
                                                key={ing.id}
                                                style={[
                                                    styles.chip,
                                                    {
                                                        backgroundColor: isSelected ? colors.primary : colors.surface,
                                                        borderColor: isSelected ? colors.primary : colors.border,
                                                    },
                                                ]}
                                                onPress={() => toggleIngredient(ing.id)}
                                            >
                                                <Text style={[styles.chipText, { color: isSelected ? '#FFF' : colors.text }]}>
                                                    {ing.name}
                                                </Text>
                                            </TouchableOpacity>
                                        );
                                    })}
                                </View>
                            </View>
                        );
                    })}
                </ScrollView>
                <View style={styles.footer}>
                    <TouchableOpacity style={[styles.primaryButton, { backgroundColor: colors.primary }]} onPress={handleNextStep}>
                        <Text style={styles.primaryButtonText}>Continue</Text>
                    </TouchableOpacity>
                </View>
            </SafeAreaView>
        );
    }

    return (
        <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
            <View style={styles.content}>
                <Text style={[styles.header, { color: colors.text }]}>Your Cooking Style</Text>
                <Text style={[styles.subHeader, { color: colors.icon }]}>Help us tailor your meal plan.</Text>

                <View style={[styles.card, { backgroundColor: colors.surface, borderColor: colors.border }]}>
                    <Text style={[styles.label, { color: colors.text }]}>Max Cooking Time</Text>
                    <Text style={[styles.value, { color: colors.primary }]}>{cookTime} minutes</Text>
                    <View style={styles.timeButtons}>
                        {[15, 30, 45, 60].map((time) => (
                            <TouchableOpacity
                                key={time}
                                style={[
                                    styles.timeChip,
                                    {
                                        backgroundColor: cookTime === time ? colors.primary : colors.background,
                                        borderColor: cookTime === time ? colors.primary : colors.border,
                                    },
                                ]}
                                onPress={() => setCookTime(time)}
                            >
                                <Text style={{ color: cookTime === time ? '#FFF' : colors.text }}>{time}m</Text>
                            </TouchableOpacity>
                        ))}
                    </View>
                </View>

                <View style={[styles.card, { backgroundColor: colors.surface, borderColor: colors.border, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }]}>
                    <View>
                        <Text style={[styles.label, { color: colors.text }]}>Batch Cook Mode</Text>
                        <Text style={[styles.description, { color: colors.icon }]}>Plan meals that provide leftovers.</Text>
                    </View>
                    <Switch
                        value={batchCook}
                        onValueChange={setBatchCook}
                        trackColor={{ false: colors.border, true: colors.secondary }}
                        thumbColor={batchCook ? colors.primary : '#f4f3f4'}
                    />
                </View>
            </View>
            <View style={styles.footer}>
                <TouchableOpacity style={[styles.secondaryButton, { borderColor: colors.primary }]} onPress={() => setStep(1)}>
                    <Text style={[styles.secondaryButtonText, { color: colors.primary }]}>Back</Text>
                </TouchableOpacity>
                <TouchableOpacity style={[styles.primaryButton, { backgroundColor: colors.primary, flex: 2 }]} onPress={handleFinishOnboarding}>
                    <Text style={styles.primaryButtonText}>Generate My Meal Plan</Text>
                </TouchableOpacity>
            </View>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1 },
    scrollContent: { padding: 24, paddingBottom: 100 },
    content: { flex: 1, padding: 24 },
    header: { fontSize: 28, fontWeight: '700', marginBottom: 8, marginTop: 24 },
    subHeader: { fontSize: 16, marginBottom: 32 },
    categoryContainer: { marginBottom: 24 },
    categoryTitle: { fontSize: 18, fontWeight: '600', marginBottom: 12 },
    chipContainer: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
    chip: {
        paddingHorizontal: 16,
        paddingVertical: 10,
        borderRadius: 20,
        borderWidth: 1,
    },
    chipText: { fontSize: 14, fontWeight: '500' },
    footer: {
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        padding: 24,
        paddingBottom: 40,
        flexDirection: 'row',
        gap: 12,
        backgroundColor: 'transparent',
    },
    primaryButton: {
        flex: 1,
        paddingVertical: 16,
        borderRadius: 12,
        alignItems: 'center',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
    },
    primaryButtonText: { color: '#FFF', fontSize: 16, fontWeight: '600' },
    secondaryButton: {
        flex: 1,
        paddingVertical: 16,
        borderRadius: 12,
        alignItems: 'center',
        borderWidth: 1,
    },
    secondaryButtonText: { fontSize: 16, fontWeight: '600' },
    card: {
        padding: 20,
        borderRadius: 16,
        borderWidth: 1,
        marginBottom: 16,
    },
    label: { fontSize: 16, fontWeight: '600', marginBottom: 4 },
    value: { fontSize: 24, fontWeight: '700', marginBottom: 16 },
    description: { fontSize: 14, marginTop: 4 },
    timeButtons: { flexDirection: 'row', gap: 8 },
    timeChip: {
        paddingHorizontal: 16,
        paddingVertical: 8,
        borderRadius: 8,
        borderWidth: 1,
    },
});
