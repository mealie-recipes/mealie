import { StyleSheet, Text, View, Switch, TouchableOpacity, ScrollView, SafeAreaView } from 'react-native';
import { useFoodStore } from '@/store/useFoodStore';
import { Colors } from '@/constants/Colors';
import { useColorScheme } from '@/hooks/useColorScheme';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';

export default function SettingsScreen() {
    const colorScheme = useColorScheme();
    const colors = Colors[colorScheme ?? 'light'];
    const router = useRouter();

    const { isAiOptimizationMode, toggleAiOptimizationMode, clearPlan } = useFoodStore();

    const handleResetApp = () => {
        useFoodStore.setState({
            hasCompletedSetup: false,
            userIngredients: [],
            generatedRecipes: [],
        });
        clearPlan();
        router.replace('/onboarding');
    };

    return (
        <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
            <View style={styles.header}>
                <Text style={[styles.headerTitle, { color: colors.text }]}>Settings</Text>
            </View>

            <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
                {/* Profile Section */}
                <View style={styles.section}>
                    <Text style={[styles.sectionTitle, { color: colors.icon }]}>PROFILE & PREFERENCES</Text>
                    <View style={[styles.card, { backgroundColor: colors.surface }]}>
                        <TouchableOpacity style={styles.row} onPress={() => router.replace('/onboarding')}>
                            <View style={styles.rowContent}>
                                <Ionicons name="restaurant-outline" size={24} color={colors.text} />
                                <Text style={[styles.rowText, { color: colors.text }]}>Update Pantry & Ingredients</Text>
                            </View>
                            <Ionicons name="chevron-forward" size={20} color={colors.icon} />
                        </TouchableOpacity>

                        <View style={styles.divider} />

                        <View style={styles.row}>
                            <View style={styles.rowContent}>
                                <Ionicons name="sparkles-outline" size={24} color={colors.text} />
                                <View>
                                    <Text style={[styles.rowText, { color: colors.text }]}>AI Shopping Optimization</Text>
                                    <Text style={[styles.rowSubtext, { color: colors.icon }]}>Round up ingredient sizes</Text>
                                </View>
                            </View>
                            <Switch
                                value={isAiOptimizationMode}
                                onValueChange={toggleAiOptimizationMode}
                                trackColor={{ false: colors.border, true: colors.secondary }}
                                thumbColor={isAiOptimizationMode ? colors.primary : '#f4f3f4'}
                            />
                        </View>
                    </View>
                </View>

                {/* Notifications */}
                <View style={styles.section}>
                    <Text style={[styles.sectionTitle, { color: colors.icon }]}>NOTIFICATIONS</Text>
                    <View style={[styles.card, { backgroundColor: colors.surface }]}>
                        <View style={styles.row}>
                            <View style={styles.rowContent}>
                                <Ionicons name="notifications-outline" size={24} color={colors.text} />
                                <Text style={[styles.rowText, { color: colors.text }]}>Meal Reminders</Text>
                            </View>
                            <Switch
                                value={true}
                                onValueChange={() => { }}
                                trackColor={{ false: colors.border, true: colors.secondary }}
                                thumbColor={colors.primary}
                            />
                        </View>
                    </View>
                </View>

                {/* Danger Zone */}
                <View style={styles.section}>
                    <Text style={[styles.sectionTitle, { color: colors.icon }]}>ACCOUNT</Text>
                    <View style={[styles.card, { backgroundColor: colors.surface }]}>
                        <TouchableOpacity style={styles.row} onPress={handleResetApp}>
                            <View style={styles.rowContent}>
                                <Ionicons name="log-out-outline" size={24} color={colors.error} />
                                <Text style={[styles.rowText, { color: colors.error }]}>Reset app and start over</Text>
                            </View>
                        </TouchableOpacity>
                    </View>
                </View>

            </ScrollView>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1 },
    header: { paddingHorizontal: 24, paddingTop: 16, paddingBottom: 16 },
    headerTitle: { fontSize: 28, fontWeight: '700' },
    scrollContent: { paddingHorizontal: 24, paddingBottom: 100 },
    section: { marginBottom: 32 },
    sectionTitle: { fontSize: 12, fontWeight: '600', marginBottom: 8, marginLeft: 16, letterSpacing: 1 },
    card: { borderRadius: 16, overflow: 'hidden' },
    row: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', padding: 16 },
    rowContent: { flexDirection: 'row', alignItems: 'center', gap: 16, flex: 1 },
    rowText: { fontSize: 16, fontWeight: '500' },
    rowSubtext: { fontSize: 12, marginTop: 2 },
    divider: { height: StyleSheet.hairlineWidth, backgroundColor: '#E2E8F0', marginLeft: 56 },
});
