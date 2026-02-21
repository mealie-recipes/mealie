import { useState } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, SafeAreaView, Modal } from 'react-native';
import { useFoodStore } from '@/store/useFoodStore';
import { Colors } from '@/constants/Colors';
import { useColorScheme } from '@/hooks/useColorScheme';
import { Recipe } from '@/store/types';
import { Ionicons } from '@expo/vector-icons';

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

export default function PlannerScreen() {
    const colorScheme = useColorScheme();
    const colors = Colors[colorScheme ?? 'light'];

    const { weeklyPlan, removeFromWeeklyPlan, generatedRecipes, addToWeeklyPlan } = useFoodStore();

    const [selectedDayToAdd, setSelectedDayToAdd] = useState<string | null>(null);

    const getDayMeals = (day: string) => weeklyPlan[day] || [];

    const handleAddMeal = (recipe: Recipe) => {
        if (selectedDayToAdd) {
            addToWeeklyPlan(selectedDayToAdd, recipe);
            setSelectedDayToAdd(null);
        }
    };

    return (
        <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
            <View style={styles.header}>
                <Text style={[styles.headerTitle, { color: colors.text }]}>Weekly Plan</Text>
                <Text style={[styles.headerSubtitle, { color: colors.icon }]}>Slot in your generated meals</Text>
            </View>

            <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
                {DAYS.map((day) => {
                    const meals = getDayMeals(day);
                    return (
                        <View key={day} style={styles.dayContainer}>
                            <View style={styles.dayHeader}>
                                <Text style={[styles.dayTitle, { color: colors.text }]}>{day}</Text>
                                <TouchableOpacity
                                    style={[styles.addButton, { backgroundColor: colors.surface, borderColor: colors.border }]}
                                    onPress={() => setSelectedDayToAdd(day)}
                                >
                                    <Ionicons name="add" size={20} color={colors.primary} />
                                </TouchableOpacity>
                            </View>

                            {meals.length === 0 ? (
                                <View style={[styles.emptyDaySlot, { borderColor: colors.border, backgroundColor: colors.surface }]}>
                                    <Text style={{ color: colors.icon }}>No meals scheduled</Text>
                                </View>
                            ) : (
                                meals.map((meal) => (
                                    <View key={meal.id} style={[styles.mealSlot, { backgroundColor: colors.surface, borderColor: colors.border }]}>
                                        <View style={{ flex: 1, marginRight: 12 }}>
                                            <Text style={[styles.mealTitle, { color: colors.text }]} numberOfLines={1}>{meal.title}</Text>
                                            <Text style={{ color: colors.icon, fontSize: 12 }}>{meal.prepTimeMinutes}m</Text>
                                        </View>
                                        <TouchableOpacity onPress={() => removeFromWeeklyPlan(day, meal.id)}>
                                            <Ionicons name="trash-outline" size={20} color={colors.error} />
                                        </TouchableOpacity>
                                    </View>
                                ))
                            )}
                        </View>
                    );
                })}
            </ScrollView>

            {/* Recipe Selection Modal */}
            <Modal visible={selectedDayToAdd !== null} animationType="slide" transparent={true}>
                <View style={styles.modalOverlay}>
                    <View style={[styles.modalContent, { backgroundColor: colors.background }]}>
                        <View style={styles.modalHeader}>
                            <Text style={[styles.modalTitle, { color: colors.text }]}>Select Meal for {selectedDayToAdd}</Text>
                            <TouchableOpacity onPress={() => setSelectedDayToAdd(null)}>
                                <Ionicons name="close" size={24} color={colors.text} />
                            </TouchableOpacity>
                        </View>
                        <ScrollView style={styles.modalList}>
                            {generatedRecipes.length === 0 ? (
                                <Text style={{ padding: 20, textAlign: 'center', color: colors.icon }}>
                                    No recipes generated yet. Go to Home to generate some!
                                </Text>
                            ) : (
                                generatedRecipes.map((recipe) => (
                                    <TouchableOpacity
                                        key={recipe.id}
                                        style={[styles.modalRecipeItem, { borderBottomColor: colors.border }]}
                                        onPress={() => handleAddMeal(recipe)}
                                    >
                                        <Text style={[styles.modalRecipeTitle, { color: colors.text }]}>{recipe.title}</Text>
                                        <Text style={{ color: colors.icon, fontSize: 12 }}>{recipe.prepTimeMinutes}m prep</Text>
                                    </TouchableOpacity>
                                ))
                            )}
                        </ScrollView>
                    </View>
                </View>
            </Modal>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1 },
    header: { paddingHorizontal: 24, paddingTop: 16, paddingBottom: 16 },
    headerTitle: { fontSize: 28, fontWeight: '700' },
    headerSubtitle: { fontSize: 16, marginTop: 4 },
    scrollContent: { paddingHorizontal: 24, paddingBottom: 100 },
    dayContainer: { marginBottom: 24 },
    dayHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
    dayTitle: { fontSize: 18, fontWeight: '600' },
    addButton: { padding: 4, borderRadius: 8, borderWidth: 1 },
    emptyDaySlot: { padding: 16, borderRadius: 12, borderWidth: 1, borderStyle: 'dashed', alignItems: 'center' },
    mealSlot: { flexDirection: 'row', alignItems: 'center', padding: 16, borderRadius: 12, borderWidth: 1, marginBottom: 8 },
    mealTitle: { fontSize: 16, fontWeight: '500', marginBottom: 4 },
    modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'flex-end' },
    modalContent: { height: '70%', borderTopLeftRadius: 24, borderTopRightRadius: 24, padding: 24 },
    modalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 },
    modalTitle: { fontSize: 20, fontWeight: '600' },
    modalList: { flex: 1 },
    modalRecipeItem: { paddingVertical: 16, borderBottomWidth: 1 },
    modalRecipeTitle: { fontSize: 16, fontWeight: '500', marginBottom: 4 },
});
