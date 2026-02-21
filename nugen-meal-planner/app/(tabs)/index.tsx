import { useEffect, useState } from 'react';
import { StyleSheet, Text, View, FlatList, Image, TouchableOpacity, ActivityIndicator, SafeAreaView } from 'react-native';
import { useFoodStore } from '@/store/useFoodStore';
import { generateRecipesFromAI } from '@/services/mockAi';
import { Colors } from '@/constants/Colors';
import { useColorScheme } from '@/hooks/useColorScheme';
import { Recipe } from '@/store/types';

export default function HomeScreen() {
  const colorScheme = useColorScheme();
  const colors = Colors[colorScheme ?? 'light'];

  const {
    userIngredients,
    userPreferences,
    generatedRecipes,
    setGeneratedRecipes,
    hasCompletedSetup,
  } = useFoodStore();

  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Auto-generate recipes if we don't have any yet and setup is complete
    if (hasCompletedSetup && generatedRecipes.length === 0) {
      handleGenerateRecipes();
    }
  }, [hasCompletedSetup]);

  const handleGenerateRecipes = async () => {
    setIsLoading(true);
    try {
      const newRecipes = await generateRecipesFromAI(userIngredients, userPreferences);
      setGeneratedRecipes(newRecipes);
    } catch (error) {
      console.error('Failed to generate recipes', error);
      alert('Failed to generate recipes. Try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  const renderRecipeCard = ({ item }: { item: Recipe }) => (
    <View style={[styles.card, { backgroundColor: colors.surface, borderColor: colors.border }]}>
      <Image source={{ uri: item.imageUrl }} style={styles.cardImage} />
      <View style={styles.cardContent}>
        <View style={styles.cardHeader}>
          <Text style={[styles.cardTitle, { color: colors.text }]} numberOfLines={2}>
            {item.title}
          </Text>
          <View style={[styles.timeTag, { backgroundColor: colors.background }]}>
            <Text style={[styles.timeText, { color: colors.icon }]}>{item.prepTimeMinutes}m</Text>
          </View>
        </View>

        <Text style={[styles.cardDescription, { color: colors.icon }]} numberOfLines={2}>
          {item.description}
        </Text>

        <View style={styles.tagsContainer}>
          {item.tags.map((tag) => (
            <View key={tag} style={[styles.tag, { backgroundColor: colors.accent + '33' }]}>
              <Text style={[styles.tagText, { color: colors.text }]}>{tag}</Text>
            </View>
          ))}
        </View>
      </View>
    </View>
  );

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
      <View style={styles.header}>
        <Text style={[styles.headerTitle, { color: colors.text }]}>Your Recipes</Text>
        <Text style={[styles.headerSubtitle, { color: colors.icon }]}>Curated from your pantry</Text>
      </View>

      {isLoading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
          <Text style={[styles.loadingText, { color: colors.text }]}>Generating your personalized meals...</Text>
        </View>
      ) : (
        <FlatList
          data={generatedRecipes}
          keyExtractor={(item) => item.id}
          renderItem={renderRecipeCard}
          contentContainerStyle={styles.listContent}
          showsVerticalScrollIndicator={false}
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Text style={[styles.emptyText, { color: colors.text }]}>No recipes found.</Text>
              <TouchableOpacity
                style={[styles.generateButton, { backgroundColor: colors.primary }]}
                onPress={handleGenerateRecipes}
              >
                <Text style={styles.generateButtonText}>Generate Recipes</Text>
              </TouchableOpacity>
            </View>
          }
          ListFooterComponent={
            generatedRecipes.length > 0 ? (
              <TouchableOpacity
                style={[styles.regenButton, { borderColor: colors.primary }]}
                onPress={handleGenerateRecipes}
              >
                <Text style={[styles.regenButtonText, { color: colors.primary }]}>Refresh Recommendations</Text>
              </TouchableOpacity>
            ) : null
          }
        />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  header: { paddingHorizontal: 24, paddingTop: 16, paddingBottom: 8 },
  headerTitle: { fontSize: 28, fontWeight: '700' },
  headerSubtitle: { fontSize: 16, marginTop: 4 },
  listContent: { padding: 24, paddingBottom: 100 },
  card: {
    borderRadius: 16,
    borderWidth: 1,
    marginBottom: 20,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  cardImage: { width: '100%', height: 160 },
  cardContent: { padding: 16 },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 },
  cardTitle: { fontSize: 18, fontWeight: '600', flex: 1, marginRight: 12 },
  timeTag: { paddingHorizontal: 8, paddingVertical: 4, borderRadius: 8 },
  timeText: { fontSize: 12, fontWeight: '500' },
  cardDescription: { fontSize: 14, lineHeight: 20, marginBottom: 16 },
  tagsContainer: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  tag: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12 },
  tagText: { fontSize: 12, fontWeight: '500' },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 24 },
  loadingText: { marginTop: 16, fontSize: 16, fontWeight: '500' },
  emptyContainer: { alignItems: 'center', marginTop: 40 },
  emptyText: { fontSize: 16, marginBottom: 16 },
  generateButton: { paddingHorizontal: 24, paddingVertical: 12, borderRadius: 8 },
  generateButtonText: { color: '#FFF', fontSize: 16, fontWeight: '600' },
  regenButton: { paddingVertical: 14, borderRadius: 12, borderWidth: 1, alignItems: 'center', marginTop: 16 },
  regenButtonText: { fontSize: 16, fontWeight: '600' },
});
