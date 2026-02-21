import { useMemo } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, SafeAreaView, Switch } from 'react-native';
import { useFoodStore } from '@/store/useFoodStore';
import { Colors } from '@/constants/Colors';
import { useColorScheme } from '@/hooks/useColorScheme';
import { Ionicons } from '@expo/vector-icons';

export default function ShoppingListScreen() {
    const colorScheme = useColorScheme();
    const colors = Colors[colorScheme ?? 'light'];

    const { weeklyPlan, isAiOptimizationMode, toggleAiOptimizationMode } = useFoodStore();

    const shoppingList = useMemo(() => {
        const list: Record<string, { quantity: number; unit: string; originalTotal: number }> = {};

        // Aggregate ingredients across all days
        Object.values(weeklyPlan).forEach((recipes) => {
            recipes.forEach((recipe) => {
                recipe.ingredients.forEach((ing) => {
                    if (!list[ing.name]) {
                        list[ing.name] = { quantity: 0, unit: ing.unit, originalTotal: 0 };
                    }
                    list[ing.name].quantity += ing.quantity;
                    list[ing.name].originalTotal += ing.quantity;
                });
            });
        });

        // Apply AI Optimization rules
        if (isAiOptimizationMode) {
            Object.keys(list).forEach((key) => {
                const item = list[key];
                // Rules mockup: Round up matching patterns
                if (item.unit === 'g') {
                    if (item.quantity > 0 && item.quantity <= 250) {
                        item.quantity = 250;
                    } else if (item.quantity > 250 && item.quantity <= 500) {
                        item.quantity = 500;
                    } else if (item.quantity > 500) {
                        item.quantity = Math.ceil(item.quantity / 500) * 500;
                    }
                }
            });
        }

        return Object.entries(list).sort((a, b) => a[0].localeCompare(b[0]));
    }, [weeklyPlan, isAiOptimizationMode]);

    const isEmpty = shoppingList.length === 0;

    return (
        <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
            <View style={styles.header}>
                <Text style={[styles.headerTitle, { color: colors.text }]}>Shopping List</Text>
                <Text style={[styles.headerSubtitle, { color: colors.icon }]}>Combined strictly from your plan</Text>
            </View>

            <View style={[styles.aiToggleContainer, { backgroundColor: colors.surface, borderColor: colors.border }]}>
                <View style={styles.aiToggleTextContainer}>
                    <Text style={[styles.aiToggleTitle, { color: colors.text }]}>
                        <Ionicons name="sparkles" size={16} color={colors.accent} /> AI Optimization Mode
                    </Text>
                    <Text style={[styles.aiToggleSubtitle, { color: colors.icon }]}>Round up to standard packaging sizes</Text>
                </View>
                <Switch
                    value={isAiOptimizationMode}
                    onValueChange={toggleAiOptimizationMode}
                    trackColor={{ false: colors.border, true: colors.secondary }}
                    thumbColor={isAiOptimizationMode ? colors.primary : '#f4f3f4'}
                />
            </View>

            {isEmpty ? (
                <View style={styles.emptyContainer}>
                    <Text style={{ color: colors.text, fontSize: 16 }}>Your list is empty. Add meals to your weekly plan!</Text>
                </View>
            ) : (
                <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
                    {shoppingList.map(([name, data]) => {
                        const hasOptimizationBuff = isAiOptimizationMode && data.quantity > data.originalTotal;
                        const diff = data.quantity - data.originalTotal;

                        return (
                            <View key={name} style={[styles.listItem, { backgroundColor: colors.surface, borderColor: colors.border }]}>
                                <View style={styles.itemHeader}>
                                    <Text style={[styles.itemName, { color: colors.text }]}>{name}</Text>
                                    <Text style={[styles.itemQuantity, { color: colors.text }]}>
                                        {data.quantity}{data.unit}
                                    </Text>
                                </View>
                                {hasOptimizationBuff && (
                                    <View style={[styles.optimizationTip, { backgroundColor: colors.accent + '22' }]}>
                                        <Text style={[styles.tipText, { color: colors.text }]}>
                                            <Ionicons name="leaf-outline" size={12} color={colors.primary} /> Bought standard {data.quantity}{data.unit} pack. Suggest using remaining {diff}{data.unit} in a quick snack!
                                        </Text>
                                    </View>
                                )}
                            </View>
                        );
                    })}
                </ScrollView>
            )}
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1 },
    header: { paddingHorizontal: 24, paddingTop: 16, paddingBottom: 16 },
    headerTitle: { fontSize: 28, fontWeight: '700' },
    headerSubtitle: { fontSize: 16, marginTop: 4 },
    aiToggleContainer: {
        marginHorizontal: 24,
        marginBottom: 24,
        padding: 16,
        borderRadius: 16,
        borderWidth: 1,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
    },
    aiToggleTextContainer: { flex: 1, marginRight: 16 },
    aiToggleTitle: { fontSize: 16, fontWeight: '600', marginBottom: 4 },
    aiToggleSubtitle: { fontSize: 12 },
    scrollContent: { paddingHorizontal: 24, paddingBottom: 100, gap: 12 },
    emptyContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', paddingHorizontal: 40 },
    listItem: { padding: 16, borderRadius: 12, borderWidth: 1 },
    itemHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
    itemName: { fontSize: 16, fontWeight: '600' },
    itemQuantity: { fontSize: 16, fontWeight: '500' },
    optimizationTip: { marginTop: 12, padding: 12, borderRadius: 8 },
    tipText: { fontSize: 12, lineHeight: 18 },
});
