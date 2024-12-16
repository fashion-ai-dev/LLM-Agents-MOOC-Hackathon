import { zodResolver } from '@hookform/resolvers/zod';
import { Paperclip } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

import { useChat } from '../../contexts/ChatContext';

import { ChatFormButton } from './ChatFormButton';

const chatFormSchema = z.object({
  message: z.string().min(1, { message: 'Message is required' }),
  image: z
    .instanceof(FileList)
    .optional()
    .refine(
      (files) => !files || files.length === 0 || files[0].size <= 5000000, // File size validation (max 5MB)
      'File size should be less than 5MB',
    )
    .refine(
      (files) =>
        !files ||
        files.length === 0 ||
        ['image/jpeg', 'image/jpg', 'image/png'].includes(files[0]?.type), // File type validation
      'Only .jpg, .jpeg, and .png files are accepted',
    ),
});

type ChatFormData = z.infer<typeof chatFormSchema>;

export function ChatForm() {
  const {
    isConnected,
    isLoading,
    isChatting,
    handleConversation,
    handleCancelConversation,
  } = useChat();

  const {
    formState: { isSubmitting, isValid },
    register,
    handleSubmit,
    reset,
  } = useForm<ChatFormData>({
    resolver: zodResolver(chatFormSchema),
    mode: 'onSubmit',
  });

  function onSubmit(data: ChatFormData) {
    handleConversation({ message: data.message, image: null });
    reset();
  }

  return (
    <div>
      <form className="relative h-[52px]" onSubmit={handleSubmit(onSubmit)}>
        <label
          htmlFor="image"
          className="pointer-events-none absolute left-6 top-1/2 h-[30px] w-[30px] -translate-y-1/2"
          hidden
        >
          <input
            type="file"
            id="image"
            accept="image/*"
            className="absolute left-0 top-0 h-0 w-0 opacity-0"
            {...register('image')}
            disabled
          />

          <span>
            <Paperclip size={30} />
          </span>
        </label>

        <input
          placeholder="Message Copilot"
          className="h-full w-full rounded-[99px] bg-[#F6F6F6] pl-[35px] pr-[55px] text-sm font-light outline-none"
          {...register('message')}
        />

        <ChatFormButton
          type="start"
          disabled={
            isSubmitting || !isValid || !isConnected || isLoading || isChatting
          }
          hidden={isChatting}
        />

        <ChatFormButton
          type="stop"
          hidden={!isChatting}
          action={handleCancelConversation}
        />
      </form>

      <p className="mt-5 text-center text-xs text-[#A5A5A5]">
        Copilot can make mistakes. Check important info.
      </p>
    </div>
  );
}
