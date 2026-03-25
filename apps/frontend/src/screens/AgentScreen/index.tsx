import React, { useState, useRef, useCallback } from 'react';
import {
    View,
    Text,
    FlatList,
    TextInput,
    TouchableOpacity,
    KeyboardAvoidingView,
    Platform,
    StatusBar,
    Modal,
    ListRenderItem,
    ImageBackground,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LiquidGlassView, isLiquidGlassSupported } from '@callstack/liquid-glass';
import { LinearGradient } from 'expo-linear-gradient';
import { Plus, SendHorizonal, Camera, Image, Link, X } from 'lucide-react-native';
import { useFocusEffect, useRoute } from '@react-navigation/native';
import ChatBubble from '../../components/ChatBubble';
import AppHeader from '../../components/AppHeader';
import { getChatSession, postChatMessage, handleFileUpload, handleActionSelection } from '../../coordinator/chatCoordinator';
import type { ChatMessage, ChatAction } from '../../coordinator/types';
import { GRADIENTS, COLORS } from '../../theme';
import styles from './styles';

// ─── Bottom Sheet attachment options ──────────────────────────────────────────
const ATTACH_CONFIG = [
    { Icon: Camera, label: 'Camera', source: 'camera' as const },
    { Icon: Image, label: 'Gallery', source: 'gallery' as const },
    { Icon: Link, label: 'Link', source: 'link' as const },
];

// ─── AgentScreen ─────────────────────────────────────────────────────────────
const AgentScreen: React.FC = () => {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [inputText, setInputText] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const [sheetOpen, setSheetOpen] = useState(false);
    const flatListRef = useRef<FlatList>(null);
    const route = useRoute<any>();

    const sessionId = 's001'; // MVP static session ID
    const activeGoalId = route.params?.activeGoalId ?? null;

    // ── Load session history on mount ─────────────────────────
    const loadSession = useCallback(async () => {
        try {
            setIsTyping(true);
            const res = await getChatSession(sessionId);
            if (res.success && res.data) {
                setMessages(res.data.messages);
            }
        } catch (error) {
            console.error('Failed to load chat session', error);
        } finally {
            setIsTyping(false);
        }
    }, [sessionId]);

    useFocusEffect(
        useCallback(() => {
            void loadSession();
        }, [loadSession]),
    );

    // ── Send a user message ───────────────────────────────────
    const handleSend = useCallback(async () => {
        const text = inputText.trim();
        if (!text) return;

        const userMsg: ChatMessage = {
            message_id: `m_${Date.now()}`,
            role: 'user',
            text,
        };

        setMessages((prev) => [...prev, userMsg]);
        setInputText('');
        setIsTyping(true);

        try {
            const res = await postChatMessage({
                session_id: sessionId,
                message: text,
                context: {
                    active_goal_id: activeGoalId,
                    source_screen: 'agent_screen',
                }
            });

            if (res.success && res.data) {
                setMessages((prev) => [...prev, res.data.reply]);
            }
        } catch (error) {
            console.error('Failed to send message', error);
        } finally {
            setIsTyping(false);
        }
    }, [activeGoalId, inputText, sessionId]);

    // ── Action button press ───────────────────────────────────
    const handleActionPress = useCallback(async (action: ChatAction) => {
        const userMsg: ChatMessage = {
            message_id: `m_${Date.now()}`,
            role: 'user',
            text: action.label,
        };

        setMessages((prev) => [...prev, userMsg]);
        setIsTyping(true);

        try {
            const selection = await handleActionSelection(action, sessionId);
            const reply = selection.reply;

            if (reply) {
                setMessages((prev) => [...prev, reply]);
            }

            if (selection.should_post_chat) {
                const res = await postChatMessage({
                    session_id: sessionId,
                    message: action.label,
                    context: {
                        active_goal_id: activeGoalId,
                        source_screen: 'agent_action',
                        ...action.payload,
                    }
                });

                if (res.success && res.data) {
                    setMessages((prev) => [...prev, res.data.reply]);
                }
            }
        } catch (error) {
            console.error('Failed to send action', error);
        } finally {
            setIsTyping(false);
        }
    }, [activeGoalId, sessionId]);

    const handleAttachOption = async (source: 'camera' | 'gallery' | 'link') => {
        setSheetOpen(false);
        await handleFileUpload(source);
    };

    const renderItem: ListRenderItem<ChatMessage> = ({ item }) => (
        <ChatBubble message={item} onActionPress={handleActionPress} />
    );

    return (
        <ImageBackground
            source={require('../../../assets/backround-01.png')}
            style={styles.root}
            resizeMode="cover"
        >
        <SafeAreaView style={{ flex: 1, backgroundColor: 'rgba(0,0,0,0.6)' }}>
            <StatusBar barStyle="light-content" backgroundColor="#000000" translucent={false} />

            <KeyboardAvoidingView
                style={{ flex: 1 }}
                behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
                keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 24}
            >
                {/* ── Centered Header ── */}
                <AppHeader subtitle="AI-Powered Financial Advisor" />

                {/* ── Message list ── */}
                <FlatList
                    ref={flatListRef}
                    data={messages}
                    keyExtractor={(item) => item.message_id}
                    renderItem={renderItem}
                    style={styles.messageList}
                    contentContainerStyle={styles.listContent}
                    onContentSizeChange={() =>
                        flatListRef.current?.scrollToEnd({ animated: true })
                    }
                    onLayout={() =>
                        flatListRef.current?.scrollToEnd({ animated: false })
                    }
                    showsVerticalScrollIndicator={false}
                    ListFooterComponent={
                        isTyping ? (
                            <View style={styles.typingRow}>
                                <Text style={styles.typingText}>GoalPilot is thinking...</Text>
                            </View>
                        ) : null
                    }
                />

                {/* ── Input bar ── */}
                <View style={styles.inputBar}>
                    {/* Plus button — opens attachment bottom sheet */}
                    <TouchableOpacity
                        style={styles.plusBtn}
                        onPress={() => setSheetOpen(true)}
                    >
                        <LiquidGlassView
                            style={[
                                styles.sendBtnGrad,
                                {
                                    borderRadius: 21,
                                    backgroundColor: 'rgba(255, 255, 255, 0.03)',
                                    borderWidth: 0.5,
                                    borderColor: 'rgba(255, 255, 255, 0.2)',
                                }
                            ]}
                            interactive
                            effect="clear"
                        >
                            <Plus size={22} color={COLORS.textPrimary} strokeWidth={2.5} />
                        </LiquidGlassView>
                    </TouchableOpacity>

                    <TextInput
                        style={styles.textInput}
                        placeholder="Ask GoalPilot anything..."
                        placeholderTextColor={COLORS.textMuted}
                        value={inputText}
                        onChangeText={setInputText}
                        multiline
                        returnKeyType="send"
                        onSubmitEditing={handleSend}
                        blurOnSubmit
                    />

                    <TouchableOpacity
                        onPress={handleSend}
                        disabled={!inputText.trim()}
                        style={styles.sendBtn}
                    >
                        <LiquidGlassView
                            style={[
                                styles.sendBtnGrad,
                                {
                                    borderRadius: 21,
                                    backgroundColor: 'rgba(255, 255, 255, 0.03)',
                                    borderWidth: 0.5,
                                    borderColor: 'rgba(223, 243, 242, 0.2)',
                                }
                            ]}
                            interactive
                            effect="clear"
                        >
                            <SendHorizonal size={20} color="#FFFFFF" strokeWidth={2.5} />
                        </LiquidGlassView>
                    </TouchableOpacity>
                </View>
            </KeyboardAvoidingView>

            {/* ── Attachment Bottom Sheet ── */}
            <Modal
                visible={sheetOpen}
                transparent
                animationType="slide"
                onRequestClose={() => setSheetOpen(false)}
            >
                <TouchableOpacity
                    style={styles.sheetOverlay}
                    activeOpacity={1}
                    onPress={() => setSheetOpen(false)}
                />
                <View style={styles.sheet}>
                    {/* Handle bar */}
                    <View style={styles.sheetHandle} />

                    <Text style={styles.sheetTitle}>Attach</Text>

                    {/* 3 option buttons */}
                    <View style={styles.sheetOptions}>
                        {ATTACH_CONFIG.map(({ Icon, label, source }) => (
                            <TouchableOpacity
                                key={label}
                                style={styles.sheetOption}
                                activeOpacity={0.82}
                                onPress={() => handleAttachOption(source)}
                            >
                                <LiquidGlassView
                                    style={[
                                        styles.sheetOptionGrad,
                                        {
                                            borderRadius: 22,
                                            backgroundColor: 'rgba(255, 255, 255, 0.05)',
                                            borderWidth: 1,
                                            borderColor: 'rgba(107, 245, 255, 0.2)'
                                        }
                                    ]}
                                    interactive
                                    effect="clear"
                                >
                                    <Icon size={26} color={COLORS.neonCyan} strokeWidth={2} />
                                </LiquidGlassView>
                                <Text style={styles.sheetOptionLabel}>{label}</Text>
                            </TouchableOpacity>
                        ))}
                    </View>

                    {/* Dismiss */}
                    <TouchableOpacity style={styles.sheetClose} onPress={() => setSheetOpen(false)}>
                        <X size={20} color={COLORS.textMuted} strokeWidth={2} />
                        <Text style={styles.sheetCloseText}>Dismiss</Text>
                    </TouchableOpacity>
                </View>
            </Modal>
        </SafeAreaView>
        </ImageBackground>
    );
};

export default AgentScreen;
