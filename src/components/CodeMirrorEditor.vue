<script setup>
import { ref, watch, onMounted } from 'vue';
import { EditorView, basicSetup } from 'codemirror';
// import { githubLight } from '@uiw/codemirror-theme-github';
import { cpp } from '@codemirror/lang-cpp';
import { python } from '@codemirror/lang-python';
import { markdown } from '@codemirror/lang-markdown';
import { Compartment } from '@codemirror/state';

const props = defineProps({
  modelValue: { type: String, default: '' },
  lang: { type: String, default: 'cpp' }, // 'cpp' | 'python' | 'md'
  editable: { type: Boolean, default: true },
  height: { type: String, default: '300px' }
});
const emit = defineEmits(['update:modelValue']);

const editorDiv = ref();
let view = null;

// compartments for reconfig
const langCompartment = new Compartment();
const editableCompartment = new Compartment();
const heightCompartment = new Compartment();

const getLangExtension = (lang) => {
  switch (lang) {
    case 'cpp': return cpp();
    case 'python': return python();
    case 'md': return markdown();
    default: return cpp();
  }
};

onMounted(() => {
  view = new EditorView({
    doc: props.modelValue,
    extensions: [
      basicSetup,
      // githubLight,
      langCompartment.of(getLangExtension(props.lang)),
      editableCompartment.of(EditorView.editable.of(props.editable)),
      heightCompartment.of(EditorView.theme({ '&': { height: props.height } })),
      EditorView.updateListener.of(update => {
        if (update.docChanged) {
          emit('update:modelValue', view.state.doc.toString());
        }
      })
    ],
    parent: editorDiv.value
  });
});

// 动态更新配置
watch(() => props.lang, (val) => {
  if (view) {
    view.dispatch({
      effects: langCompartment.reconfigure(getLangExtension(val))
    });
  }
});

watch(() => props.editable, (val) => {
  if (view) {
    view.dispatch({
      effects: editableCompartment.reconfigure(EditorView.editable.of(val))
    });
  }
});

watch(() => props.height, (val) => {
  if (view) {
    view.dispatch({
      effects: heightCompartment.reconfigure(EditorView.theme({ '&': { height: val } }))
    });
  }
});

// 外部 modelValue 变化时更新编辑器
watch(() => props.modelValue, (val) => {
  if (view && val !== view.state.doc.toString()) {
    view.dispatch({
      changes: { from: 0, to: view.state.doc.length, insert: val }
    });
  }
});
</script>

<template>
  <div ref="editorDiv" />
</template>
