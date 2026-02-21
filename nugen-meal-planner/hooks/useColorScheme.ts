import { useColorScheme as _useColorScheme } from 'react-native';

export function useColorScheme(): 'light' | 'dark' {
    const colorScheme = _useColorScheme();
    return colorScheme ?? 'light';
}
