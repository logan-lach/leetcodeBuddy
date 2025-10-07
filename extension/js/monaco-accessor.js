// Monaco Editor Accessor
// This script runs in the page context (not isolated) to access window.monaco
// It communicates with the content script via custom events

(function() {
  'use strict';

  console.log('[Monaco Accessor] Script loaded in page context');

  // Function to get Monaco editor value
  function getMonacoEditorValue() {
    try {
      console.log('[Monaco Accessor] Attempting to get Monaco editor value');

      // Check if monaco is available
      if (typeof monaco === 'undefined') {
        console.warn('[Monaco Accessor] monaco is undefined');
        console.log('[Monaco Accessor] window.monaco:', window.monaco);
        console.log('[Monaco Accessor] Available on window:', Object.keys(window).filter(k => k.toLowerCase().includes('monaco')));
        return null;
      }

      if (!monaco.editor) {
        console.warn('[Monaco Accessor] monaco.editor is undefined');
        console.log('[Monaco Accessor] monaco object keys:', Object.keys(monaco));
        return null;
      }

      console.log('[Monaco Accessor] monaco.editor is available');
      console.log('[Monaco Accessor] monaco.editor keys:', Object.keys(monaco.editor));

      // Try to get editor instance from models
      const models = monaco.editor.getModels();
      console.log('[Monaco Accessor] Models count:', models?.length || 0);
      if (models && models.length > 0) {
        console.log('[Monaco Accessor] Model 0 info:', {
          uri: models[0].uri?.toString(),
          lineCount: models[0].getLineCount(),
          languageId: models[0].getLanguageId()
        });
      }

      if (models && models.length > 0) {
        const code = models[0].getValue();
        console.log('[Monaco Accessor] Code retrieved from model, length:', code?.length || 0);
        console.log('[Monaco Accessor] First 100 chars:', code?.substring(0, 100));
        return code;
      }

      // Alternative: Try to get from editors
      const editors = monaco.editor.getEditors();
      console.log('[Monaco Accessor] Editors count:', editors?.length || 0);

      if (editors && editors.length > 0) {
        console.log('[Monaco Accessor] Editor 0 methods:', Object.keys(editors[0]).filter(k => typeof editors[0][k] === 'function'));
        const code = editors[0].getValue();
        console.log('[Monaco Accessor] Code retrieved from editor, length:', code?.length || 0);
        return code;
      }

      console.warn('[Monaco Accessor] No models or editors found');

      // Try alternative methods to find the editor
      console.log('[Monaco Accessor] Checking for alternative access methods...');
      if (window.monaco && window.monaco.editor) {
        const editorKeys = Object.keys(window.monaco.editor);
        console.log('[Monaco Accessor] All monaco.editor keys:', editorKeys);
      }

      return null;
    } catch (error) {
      console.error('[Monaco Accessor] Error accessing Monaco editor:', error);
      console.error('[Monaco Accessor] Error stack:', error.stack);
      return null;
    }
  }

  // Listen for requests from content script
  window.addEventListener('LEETCODE_BUDDY_GET_MONACO_CODE', function(event) {
    console.log('[Monaco Accessor] Received request for Monaco code');
    const code = getMonacoEditorValue();
    console.log('[Monaco Accessor] Sending response with code:', code ? 'SUCCESS' : 'NULL');

    // Send response back to content script
    window.dispatchEvent(new CustomEvent('LEETCODE_BUDDY_MONACO_CODE_RESPONSE', {
      detail: { code: code }
    }));
  });

  // Signal that the accessor is ready
  console.log('[Monaco Accessor] Sending ready signal');
  window.dispatchEvent(new CustomEvent('LEETCODE_BUDDY_MONACO_ACCESSOR_READY'));
})();
