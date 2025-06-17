using System;

namespace TestRepo
{
    public class MultipleInterfaces : IReadable, IWritable, IProcessable
    {
        private string data;

        public MultipleInterfaces(string data)
        {
            this.data = data;
        }

        public string Read()
        {
            return data;
        }

        public void Write(string data)
        {
            this.data = data;
        }

        public void Process()
        {
            Console.WriteLine($"Processing data: {data}");
        }

        public string GetType()
        {
            return "MultipleInterfaces";
        }
    }
}