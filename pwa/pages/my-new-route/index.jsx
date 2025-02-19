import React, { useEffect, useRef } from 'react';

const WebChatComponent = () => {
  const webchatRef = useRef(null);

  useEffect(() => {
    const loadWebChat = () => {
      console.log('✅ WebChat script loaded.');

      // 🚀 加载 ESM 兼容的 DirectLine
      const directLineScript = document.createElement('script');
      directLineScript.src = 'https://cdn.jsdelivr.net/npm/botframework-directlinejs@latest/dist/directline.js?module';
      directLineScript.async = true;
      directLineScript.onload = () => {
        console.log('✅ DirectLine script loaded.');

        // 🔥 确保 `window.DirectLine` 正确加载
        const waitForDirectLine = setInterval(() => {
          if (window.DirectLine && window.DirectLine.DirectLine) {
            clearInterval(waitForDirectLine);
            initializeWebChat();
          }
        }, 100);
      };

      document.body.appendChild(directLineScript);
    };

    const initializeWebChat = () => {
      console.log("✅ 初始化 WebChat");

      // ✅ 现在 `window.DirectLine` 已经可用
      const directLine = new window.DirectLine.DirectLine({
        token: "BPcD5WqGsIt6CFPp4QGDL5IUnnRgwsSiJzgMkav2FxvtR2CCqnI5JQQJ99BBAC5RqLJAArohAAABAZBS2oHr.AnpRKAA7s3ZZoDt0oE164ULNOvdFFOmQt6JcrszEm5cSEvURkZV6JQQJ99BBAC3pKaRAArohAAABAZBS2yrh",
        userId: "c48bc895-40be-4e58-9e65-bcabdbf943e4",
        pollingInterval: 2000
      });

      // ✅ 自定义 Middleware
      const store = window.WebChat.createStore({}, ({ dispatch }) => (next) => (action) => {
        if (action.type === 'DIRECT_LINE/INCOMING_ACTIVITY') {
          console.log('📩 收到消息:', action.payload.activity);
        }
        return next(action);
      });

      // ✅ 自定义 WebChat UI 样式
      const styleOptions = {
        botAvatarInitials: '🤖',
        userAvatarInitials: '👤',
        backgroundColor: '#f5f5f5',
        bubbleBackground: '#0078D7',
        bubbleTextColor: 'white',
        bubbleBorderRadius: 10,
      };

      // ✅ 渲染 WebChat
      if (window.WebChat && webchatRef.current) {
        window.WebChat.renderWebChat(
          {
            directLine,
            userID: "c48bc895-40be-4e58-9e65-bcabdbf943e4",
            store,
            styleOptions
          },
          webchatRef.current
        );
      }
    };

    // 🚀 先加载 WebChat
    const script = document.createElement('script');
    script.src = 'https://cdn.botframework.com/botframework-webchat/latest/webchat.js';
    script.async = true;
    script.onload = loadWebChat;
    document.body.appendChild(script);
  }, []);

  return <div ref={webchatRef} style={{ width: '100%', height: '500px' }} />;
};

export default WebChatComponent;
